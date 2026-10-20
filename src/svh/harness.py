"""Configure the existing deepagents loop; never construct an implicit model."""
from deepagents import (create_deep_agent, register_harness_profile, HarnessProfile,
                        GeneralPurposeSubagentProfile)
from deepagents._models import get_model_identifier, get_model_provider
from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

from svh.docker_backend import DockerSandbox


class NoDelegation(AgentMiddleware):
    """Deny dispatch even if a model fabricates an unadvertised task call."""
    @staticmethod
    def denied(request):
        if request.tool_call["name"] == "task":
            return ToolMessage(content="Delegation is disabled for this budgeted run.",
                               tool_call_id=request.tool_call["id"], status="error")
        return None

    def wrap_tool_call(self, request, handler):
        denied = self.denied(request)
        return denied if denied is not None else handler(request)

    async def awrap_tool_call(self, request, handler):
        denied = self.denied(request)
        return denied if denied is not None else await handler(request)


def create_harness(model, backend, *, tools=(), system_prompt, response_format=None):
    if not isinstance(backend, DockerSandbox):
        raise ValueError("Generated commands require the Docker sandbox backend")
    if backend.closed:
        raise ValueError("Start the isolated sandbox before constructing its agent")
    provider, identifier = get_model_provider(model), get_model_identifier(model)
    if not provider or not identifier:
        raise ValueError("An explicitly identified model instance is required")
    register_harness_profile(f"{provider}:{identifier}", HarnessProfile(
        general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False),
        excluded_tools=frozenset({"task"}),
    ))
    return create_deep_agent(model=model, backend=backend, tools=list(tools), subagents=[],
        middleware=[NoDelegation()], system_prompt=system_prompt, response_format=response_format)
