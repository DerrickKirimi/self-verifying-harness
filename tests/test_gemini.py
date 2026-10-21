import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

pytest.importorskip("langchain_google_genai")
from google.genai.types import GenerateContentResponse
from langsmith import tracing_context

from svh.budget import Budget, BudgetExceeded, token_cost
from svh.gemini import Price, model, private_values


def setup(tmp_path, cap="4",tier='standard'):
    budget = Budget(tmp_path / "budget.db", cap)
    rates=('.15','1.25') if tier=='flex' else ('.30','2.50')
    price = Price("gemini-3.5-flash-lite", *rates, datetime.now(timezone.utc), 1_048_576, 65_536,tier)
    return model(api_key="test-not-a-key", budget=budget, price=price), budget


def response(metered=True):
    return GenerateContentResponse(
        candidates=[{"content": {"role": "model", "parts": [{"text": "done"}]}, "finish_reason": "STOP"}],
        usage_metadata={"prompt_token_count": 20, "candidates_token_count": 5,
                        "thoughts_token_count": 7, "total_token_count": 32} if metered else None,
    )


def test_all_public_transports_and_bound_tools_are_metered(tmp_path):
    instance, budget = setup(tmp_path)
    calls = []

    def generate(**request):
        # Assert reserve happened before touching the provider transport.
        assert budget.summary()["unsettled_requests"] == 1
        assert request["config"].http_options.retry_options.attempts == 1
        calls.append(request)
        return response()

    async def agenerate(**request):
        return generate(**request)

    async def exercise():
        assert (await instance.ainvoke("hello")).text == "done"
        assert len([chunk async for chunk in instance.astream("hello")]) == 1

    with tracing_context(enabled=False), patch.object(instance.client.models, "generate_content", side_effect=generate), patch.object(instance.async_client.models, "generate_content", side_effect=agenerate):
        assert instance.invoke("hello").usage_metadata["output_tokens"] == 12
        assert len(list(instance.stream("hello"))) == 1
        tool = {"name": "lookup", "description": "Read evidence", "parameters": {"type": "object", "properties": {}}}
        instance.bind_tools([tool]).invoke("hello")
        asyncio.run(exercise())
    assert len(calls) == 5
    assert budget.summary()["unsettled_requests"] == 0
    assert budget.summary()["charged_or_reserved_microdollars"] == 5 * token_cost(20, 12, ".30", "2.50")


@pytest.mark.parametrize("kind", ["timeout", "missing_usage"])
def test_ambiguous_result_keeps_full_reservation(tmp_path, kind):
    instance, budget = setup(tmp_path)
    with tracing_context(enabled=False), patch.object(instance.client.models, "generate_content", side_effect=TimeoutError() if kind == "timeout" else None, return_value=response(False)) as provider:
        with pytest.raises((TimeoutError, ValueError)):
            instance.invoke("hello")
    assert provider.call_count == 1
    assert budget.summary()["unsettled_requests"] == 1
    assert budget.summary()["charged_or_reserved_microdollars"] == token_cost(1_048_576, 4096, ".30", "2.50")


def test_exhaustion_and_expiry_make_no_provider_call(tmp_path):
    instance, _ = setup(tmp_path, ".01")
    with tracing_context(enabled=False), patch.object(instance.client.models, "generate_content") as provider:
        with pytest.raises(BudgetExceeded):
            instance.invoke("hello")
        assert not provider.called
    stale = Price("test", ".3", "2.5", datetime.now(timezone.utc) - timedelta(days=2), 10, 10)
    with pytest.raises(ValueError, match="24 hours"):
        stale.validate()


def test_actual_summary_middleware_uses_guard_and_does_not_retry_timeout(tmp_path):
    from langchain.agents.middleware.summarization import SummarizationMiddleware
    from langchain_core.messages import HumanMessage
    instance, budget = setup(tmp_path)
    middleware = SummarizationMiddleware(model=instance, trigger=("messages", 2), keep=("messages", 1))
    with tracing_context(enabled=False), patch.object(instance.client.models, "generate_content", return_value=response()) as provider:
        assert middleware._create_summary([HumanMessage(content="earlier context")]) == "done"
        assert provider.call_count == 1
    assert budget.summary()["unsettled_requests"] == 0
    with tracing_context(enabled=False), patch.object(instance.client.models, "generate_content", side_effect=TimeoutError()) as provider:
        with pytest.raises(TimeoutError):
            middleware._create_summary([HumanMessage(content="earlier context")])
        assert provider.call_count == 1
    assert budget.summary()["unsettled_requests"] == 1
    async def timeout(**request):
        raise TimeoutError()
    with tracing_context(enabled=False), patch.object(instance.async_client.models, "generate_content", side_effect=timeout) as provider:
        with pytest.raises(TimeoutError):
            asyncio.run(middleware._acreate_summary([HumanMessage(content="earlier context")]))
        assert provider.call_count == 1
    assert budget.summary()["unsettled_requests"] == 2


@pytest.mark.parametrize("override", [
    {"max_output_tokens": 5000}, {"n": 2}, {"cached_content": "cache/123"},
    {"tools": [{"google_search": {}}]}, {"response_modalities": ["IMAGE"]},
])
def test_unbudgeted_request_options_never_reach_provider(tmp_path, override):
    instance, _ = setup(tmp_path)
    with tracing_context(enabled=False), patch.object(instance.client.models, "generate_content") as provider:
        with pytest.raises(ValueError):
            instance.invoke("hello", **override)
        assert not provider.called


def test_private_configuration_is_literal_and_rejects_permissions_and_symlinks(tmp_path):
    config = tmp_path / "config"
    config.write_text("KEY=$(touch /tmp/should-not-exist)\n")
    config.chmod(0o600)
    assert private_values(config)["KEY"] == "$(touch /tmp/should-not-exist)"
    config.chmod(0o644)
    with pytest.raises(ValueError):
        private_values(config)
    link = tmp_path / "link"
    link.symlink_to(config)
    with pytest.raises(OSError):
        private_values(link)


def test_flex_pins_tier_full_context_reservation_and_timeout(tmp_path):
    instance,budget=setup(tmp_path,tier='flex')
    def generate(**request):
        assert request['config'].service_tier=='flex'
        assert request['config'].http_options.timeout==900000
        assert request['config'].http_options.retry_options.attempts==1
        assert budget.summary()['charged_or_reserved_microdollars']==token_cost(1048576,4096,'.15','1.25')
        return response()
    with tracing_context(enabled=False),patch.object(instance.client.models,'generate_content',side_effect=generate):
        instance.invoke('controlled request')
    assert budget.summary()['charged_or_reserved_microdollars']==token_cost(20,12,'.15','1.25')


@pytest.mark.parametrize('override',['standard','priority','auto'])
def test_flex_cannot_upgrade_through_bound_arguments(tmp_path,override):
    instance,budget=setup(tmp_path,tier='flex')
    with tracing_context(enabled=False),patch.object(instance.client.models,'generate_content') as provider:
        with pytest.raises(ValueError,match='tier override'):
            instance.bind(service_tier=override).invoke('controlled')
        assert not provider.called


def test_flex_timeout_never_retries_or_falls_back_to_standard(tmp_path):
    instance,budget=setup(tmp_path,tier='flex')
    with tracing_context(enabled=False),patch.object(instance.client.models,'generate_content',side_effect=TimeoutError()) as provider:
        with pytest.raises(TimeoutError):instance.invoke('controlled')
        assert provider.call_count==1
    assert budget.summary()['charged_or_reserved_microdollars']==token_cost(1048576,4096,'.15','1.25')
    assert budget.summary()['unsettled_requests']==1
