import pytest
pytest.importorskip("deepagents")

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langsmith import tracing_context
from pydantic import PrivateAttr

from svh.docker_backend import DockerSandbox
from deepagents.backends.protocol import ExecuteResponse
from svh.harness import create_harness


class ControlledModel(BaseChatModel):
    model_name: str = "controlled"
    attempt_delegation: bool = False
    _advertised: list = PrivateAttr(default_factory=list)
    @property
    def _llm_type(self):
        return "svh-controlled"
    def _get_ls_params(self, **kwargs):
        return {"ls_provider": "svh-controlled", "ls_model_name": self.model_name}
    def bind_tools(self, tools, **kwargs):
        self._advertised = [tool.name if hasattr(tool, "name") else tool["name"] for tool in tools]
        return self.bind(tools=tools, **kwargs)
    def _generate(self, messages, **kwargs):
        if any(isinstance(message, ToolMessage) for message in messages):
            message = AIMessage(content="Checkpoint complete.")
        else:
            name = "task" if self.attempt_delegation else "execute"
            args = {"description": "Unwanted worker", "subagent_type": "general-purpose"} if self.attempt_delegation else {"command": "printf controlled"}
            message = AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": "controlled-call"}])
        return ChatResult(generations=[ChatGeneration(message=message)])


class ControlledBackend(DockerSandbox):
    """A workflow double; real isolation is measured by smoke_docker_backend.py."""
    def __init__(self):
        super().__init__("sha256:" + "a" * 64, "b" * 40)
        self.closed = False
        self.calls = []
    def execute(self, command, *, timeout=None):
        self.calls.append(command)
        return ExecuteResponse(output="controlled-container-response", exit_code=0)


@pytest.mark.parametrize("delegation", [False, True])
def test_existing_agent_dispatches_only_to_backend_and_cannot_delegate(delegation):
    backend = ControlledBackend()
    model = ControlledModel(attempt_delegation=delegation)
    with tracing_context(enabled=False):
        agent = create_harness(model, backend, system_prompt="Inspect code in the sandbox.")
        result = agent.invoke({"messages": [{"role": "user", "content": "Inspect the source."}]}, config={"recursion_limit": 8})
    assert "task" not in model._advertised
    replies = [message for message in result["messages"] if isinstance(message, ToolMessage)]
    assert len(replies) == 1
    if delegation:
        assert replies[0].status == "error" and not backend.calls
    else:
        assert replies[0].status == "success" and backend.calls == ["printf controlled"]


def test_harness_rejects_a_host_or_implicit_backend():
    with pytest.raises(ValueError, match="Docker"):
        create_harness(ControlledModel(), None, system_prompt="Inspect code")
    with pytest.raises(ValueError, match="immutable"):
        DockerSandbox("latest", "main")
