"""Budget-covered Developer API model, including direct middleware invocations.

No model loop lives here. Unknown request outcomes retain their reservation.
Only the factory below should construct the production model.
"""

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import os
import json
from pathlib import Path
import stat

from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import PrivateAttr

from svh.budget import Budget, token_cost


def private_values(path: Path):
    """Read literal KEY=value secrets without executing shell or dotenv expansion."""
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    with os.fdopen(fd) as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("Configuration must be an owner-only regular file")
        values = {}
        for line in stream:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, separator, value = line.partition("=")
            if not separator or not key.isidentifier() or key in values:
                raise ValueError("Invalid literal configuration")
            values[key] = value.strip().removeprefix('"').removesuffix('"').removeprefix("'").removesuffix("'")
        return values


@dataclass(frozen=True)
class Price:
    model: str
    input_rate: str
    output_rate: str
    checked_at: datetime
    input_limit: int
    output_limit: int
    service_tier: str = 'standard'

    def validate(self):
        age = datetime.now(timezone.utc) - self.checked_at
        if not timedelta(0) <= age <= timedelta(hours=24):
            raise ValueError("Model limits and prices require a review within 24 hours")
        if any(type(n) is not int or n <= 0 for n in (self.input_limit, self.output_limit)):
            raise ValueError("Authenticated model token limits are required")
        if self.service_tier not in {'standard','flex'}:
            raise ValueError('Unreviewed service tier')
        token_cost(1, 1, self.input_rate, self.output_rate)


class BudgetedGemini(ChatGoogleGenerativeAI):
    _budget: Budget = PrivateAttr()
    _price: Price = PrivateAttr()
    _output_cap: int = PrivateAttr()

    def with_retry(self, **kwargs):
        # SummarizationMiddleware installs a Runnable retry wrapper itself.
        # Keep that path covered, but never resubmit an ambiguous paid request.
        kwargs["stop_after_attempt"] = 1
        return super().with_retry(**kwargs)

    def _prepare_request(self, *args, **kwargs):
        modalities = kwargs.get("response_modalities")
        if modalities and any(getattr(value, "value", value) != "TEXT" for value in modalities):
            raise ValueError("Only text generation is budgeted")
        request = super()._prepare_request(*args, **kwargs)
        config = request["config"]
        allowed = {"http_options", "system_instruction", "temperature", "top_p", "top_k",
                   "candidate_count", "max_output_tokens", "stop_sequences", "seed",
                   "presence_penalty", "frequency_penalty", "response_mime_type",
                   "response_schema", "response_json_schema", "response_modalities",
                   "safety_settings", "tools", "tool_config", "thinking_config", "service_tier"}
        if set(config.model_dump(exclude_none=True)) - allowed:
            raise ValueError("Unreviewed provider configuration is disabled")
        for content in request["contents"]:
            for part in content.parts or []:
                if set(part.model_dump(exclude_none=True)) - {"text", "thought", "thought_signature", "inline_data", "function_call", "function_response"}:
                    raise ValueError("Only inline evidence and local function tools are enabled")
                if part.inline_data and part.inline_data.mime_type not in {"image/png", "image/jpeg", "audio/wav"}:
                    raise ValueError("Unsupported inline media type")
        # Validate the final SDK request, including bind()/bind_tools() overrides.
        if request["model"].removeprefix("models/") != self._price.model:
            raise ValueError("Model override is forbidden")
        if config.candidate_count not in (None, 1):
            raise ValueError("Only one candidate is budgeted")
        if config.cached_content or config.image_config or config.response_modalities not in (None, ["TEXT"]):
            raise ValueError("Only uncached text generation is enabled")
        for tool in config.tools or []:
            fields = tool.model_dump(exclude_none=True)
            if set(fields) != {"function_declarations"}:
                raise ValueError("Provider-hosted tools are not budgeted")
        if config.max_output_tokens != self._output_cap:
            raise ValueError("Output token cap override is forbidden")
        if config.service_tier not in (None,self._price.service_tier):
            raise ValueError('Service tier override is forbidden')
        config.service_tier='flex' if self._price.service_tier=='flex' else None
        # Force a single network attempt and the official Developer API endpoint.
        from google.genai.types import HttpOptions, HttpRetryOptions
        config.http_options = HttpOptions(timeout=900_000 if self._price.service_tier=='flex' else 120_000,
                                         retry_options=HttpRetryOptions(attempts=1))
        return request

    def _reserve(self):
        self._price.validate()
        transport = self.client._api_client
        if (not self.disable_streaming or self._use_vertexai or transport.vertexai
                or transport._http_options.base_url != "https://generativelanguage.googleapis.com"):
            raise ValueError("Streaming and Vertex AI are disabled")
        return self._budget.reserve(token_cost(
            self._price.input_limit, self._output_cap,
            self._price.input_rate, self._price.output_rate), label=self._price.model+':'+self._price.service_tier)

    def _settle(self, reservation, result):
        if len(result.generations) != 1:
            raise ValueError("Missing single metered generation; reservation retained")
        usage = result.generations[0].message.usage_metadata
        if not usage or "input_tokens" not in usage or "output_tokens" not in usage:
            raise ValueError("Missing metered usage; reservation retained")
        # LangChain's output_tokens includes thoughts_token_count already.
        self._budget.settle(reservation, token_cost(
            usage["input_tokens"], usage["output_tokens"],
            self._price.input_rate, self._price.output_rate))
        return result

    def _generate(self, *args, **kwargs):
        reservation = self._reserve()
        return self._settle(reservation, super()._generate(*args, **kwargs))

    async def _agenerate(self, *args, **kwargs):
        reservation = self._reserve()
        return self._settle(reservation, await super()._agenerate(*args, **kwargs))

    def _stream(self, *args, **kwargs):
        raise ValueError("Provider streaming is disabled; use invoke")

    async def _astream(self, *args, **kwargs):
        raise ValueError("Provider streaming is disabled; use ainvoke")
        yield  # Async generator contract; never reached.


def model(*, api_key: str, budget: Budget, price: Price, output_cap=4096):
    price.validate()
    if not api_key or type(output_cap) is not int or not 0 < output_cap <= price.output_limit:
        raise ValueError("Explicit credentials and a valid output cap are required")
    instance = BudgetedGemini(
        model=price.model, api_key=api_key, vertexai=False,
        base_url="https://generativelanguage.googleapis.com", api_version="v1beta",
        max_retries=0, timeout=120_000, max_output_tokens=output_cap,
        n=1, disable_streaming=True, cache=False,
    )
    instance._budget, instance._price, instance._output_cap = budget, price, output_cap
    if instance.client._api_client.vertexai:
        instance.client.close()
        raise ValueError("Developer API required; ambient Vertex configuration rejected")
    return instance


def configured_model(root: Path, name="gemini-3.5-flash-lite", output_cap=4096, *, service_tier='standard'):
    """Use only the authorized secret pointer, reviewed prices and shared ledger."""
    config = private_values(root / ".env")
    secrets = private_values(Path(config["SVH_GEMINI_SECRETS_FILE"]))
    metadata = json.loads((root / "notes/runs/gemini-model-metadata.json").read_text())
    from svh.model_policy import reviewed_access
    policy_bytes = (root / 'notes/runs/gemini-price-policy.json').read_bytes()
    entry, rates, checked = reviewed_access(policy_bytes, metadata, name, service_tier)
    price = Price(name, *rates, checked, entry["input_limit"], entry["output_limit"], service_tier)
    from decimal import Decimal
    # A higher config value never raises an existing ledger; explicit owner
    # funding must first be recorded through Budget.authorize_limit.
    cap = Decimal(config["SVH_API_CAP_USD"])
    return model(api_key=secrets.get("GEMINI_API_KEY") or secrets.get("GOOGLE_API_KEY"),
                 budget=Budget(root / "data/runtime/gemini-budget.sqlite", cap),
                 price=price, output_cap=output_cap)
