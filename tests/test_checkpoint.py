import asyncio
import json
from types import SimpleNamespace

import pytest
pytest.importorskip("deepagents")
from langchain_core.messages import AIMessage, ToolMessage
from svh import checkpoint


def test_issue_only_schema_cannot_supply_placeholder_media_evidence():
    from pydantic import ValidationError
    prediction = {"id": "claim-1", "symptom": "reported bug", "expected_behavior": "reported rule",
                  "expected_source": "issue", "uncertainty": None}
    result = {"code_evidence": [], "hypotheses": [], "questions": [], "refined_predictions": [prediction]}
    canonical = checkpoint.canonical_output(result, "issue-only")
    assert canonical["refined_predictions"][0]["span"] is None
    assert canonical["refined_predictions"][0]["observations"] == []
    prediction["span"] = {"start_s": 0, "end_s": 0}
    with pytest.raises(ValidationError):
        checkpoint.canonical_output(result, "issue-only")


@pytest.mark.parametrize("changed", [False, True])
def test_checkpoint_binds_real_source_and_refuses_edits(tmp_path, monkeypatch, changed):
    result = {"code_evidence": [{"path": "/workspace/lib/handler.js", "line": 1, "observation": "existing code"}],
              "hypotheses": ["possible cause"], "questions": [], "refined_predictions": []}
    messages = [ToolMessage(content="metadata", name="get_recording", tool_call_id="1", artifact={"duration_s": 3}),
                ToolMessage(content="frames", name="get_frames", tool_call_id="f1", artifact={"timestamps_s": [.1, .5]}),
                ToolMessage(content="frames", name="get_frames", tool_call_id="f2", artifact={"timestamps_s": [1, 2]}),
                ToolMessage(content="source", name="read_file", tool_call_id="2"), AIMessage(content=json.dumps(result))]
    class Agent:
        async def astream(self, *args, **kwargs):
            yield {"messages": messages, "structured_response": checkpoint.CheckpointOutput.model_validate(result)}
    class Backend:
        initial_source_fingerprint = "before"
        image = "immutable-image"
        base_commit = "base"
        source_archive_sha256 = "archive"
        def source_fingerprint(self):
            return "after" if changed else "before"
        def download_files(self, paths):
            return [SimpleNamespace(error=None, content=b"actual source line\n")]
    async def tools(client):
        return []
    monkeypatch.setattr(checkpoint, "harness_tools", tools)
    monkeypatch.setattr(checkpoint, "create_harness", lambda *args, **kwargs: Agent())
    destination = tmp_path / "trace.json"
    call = checkpoint.inspect_code({"id": "case", "problem_statement": "public issue"}, {"predictions": []},
        SimpleNamespace(model="controlled"), Backend(), None, destination)
    if changed:
        with pytest.raises(ValueError, match="changed source"):
            asyncio.run(call)
    else:
        scored = asyncio.run(call)
        assert scored["source_unchanged"]
        assert scored["code_evidence"][0]["actual_line"] == "actual source line"
        assert len(scored["code_evidence"][0]["file_sha256"]) == 64
    assert destination.exists()  # Failed checkpoints retain the exact episode too.
