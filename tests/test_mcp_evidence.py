"""Actual HTTP/SDK boundary, adversarial inputs and existing-harness tool flow."""

import asyncio
import hashlib
import json
from pathlib import Path
import shutil
import socket
import subprocess

import pytest

pytest.importorskip("mcp")

import httpx2
import uvicorn
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from svh.evidence import Evidence, Recording
from svh.mcp_client import connect, harness_tools
from svh.mcp_server import build_app, private_token


@pytest.fixture
def evidence(tmp_path):
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg is required for recording evidence")
    media = tmp_path / "controlled.mp4"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                    "color=c=red:s=32x32:d=2", "-c:v", "mpeg4", str(media)], check=True, timeout=20)
    record = Recording("controlled", media, hashlib.sha256(media.read_bytes()).hexdigest(),
                       2.0, False, "video", "https://example.com/controlled.mp4")
    index = {"identity": {"recording_id": record.id, "media_sha256": record.sha256,
                           "corpus_sha256": "a" * 64},
             "frames": [{"timestamp_s": (n + .5) * 2 / 45, "caption": "red screen",
                          "screen_text": "Controlled"} for n in range(45)]}
    return Evidence([record], "a" * 64, visual_indexes={record.id: index})


def test_frame_inputs_cannot_change_trusted_media_or_escape_bounds(evidence):
    for recording, start, end, count in [("../../.env", 0, 1, 1), ("controlled", -1, 1, 1),
                                          ("controlled", 0, 3, 1), ("controlled", 0, float("nan"), 1),
                                          ("controlled", 0, 1, 100)]:
        with pytest.raises(ValueError):
            evidence.frames(recording, start, end, count)
    record = evidence.recording("controlled")
    record.path.write_bytes(b"changed-after-registration")
    with pytest.raises(ValueError, match="bytes changed"):
        evidence.frames("controlled", 0, 1, 1)


def test_token_is_private_and_refuses_public_permissions(tmp_path):
    path = tmp_path / "token"
    token = private_token(path)
    assert private_token(path) == token
    assert path.stat().st_mode & 0o777 == 0o600
    path.chmod(0o644)
    with pytest.raises(ValueError, match="owner-only"):
        private_token(path)


class OneToolModel(BaseChatModel):
    """A deterministic test double, never a substitute for model evaluation."""
    @property
    def _llm_type(self):
        return "svh-test-double"

    def bind_tools(self, tools, **kwargs):
        return self.bind(tools=tools, **kwargs)

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        if any(isinstance(message, ToolMessage) for message in messages):
            message = AIMessage(content="Observed registered recording metadata.")
        else:
            message = AIMessage(content="", tool_calls=[{"name": "get_recording", "args": {
                "recording_id": "controlled"}, "id": "metadata-call"}])
        return ChatResult(generations=[ChatGeneration(message=message)])


def test_real_http_sdk_images_prompts_resources_and_deepagents(evidence):
    async def run():
        from deepagents import create_deep_agent
        from langsmith import tracing_context

        token = "t" * 43
        sock = socket.socket()
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(build_app(evidence, token), log_level="error", access_log=False))
        task = asyncio.create_task(server.serve(sockets=[sock]))
        try:
            async with asyncio.timeout(10):
                while not server.started:
                    if task.done():
                        await task
                    await asyncio.sleep(0.01)
            url = f"http://127.0.0.1:{port}/mcp"
            async with httpx2.AsyncClient() as raw:
                assert (await raw.get(url)).status_code == 401
                origin = await raw.get(url, headers={"Authorization": "Bearer " + token,
                    "Origin": "https://outside.invalid", "Accept": "application/json, text/event-stream"})
                assert origin.status_code in (400, 403) and "origin" in origin.text.lower()
            async with connect(url, token) as client:
                assert client.protocol_version == "2026-07-28"
                tools = (await client.list_tools()).tools
                frames_schema = next(tool.input_schema for tool in tools if tool.name == "get_frames")
                assert set(frames_schema["properties"]) == {"recording_id", "t0", "t1", "max_frames"}
                assert "path" not in frames_schema["properties"]
                metadata = await client.call_tool("get_recording", {"recording_id": "controlled"})
                assert not metadata.is_error, metadata.model_dump()
                assert metadata.structured_content is not None, metadata.model_dump()
                assert metadata.structured_content["id"] == "controlled"
                assert "path" not in metadata.structured_content
                frames = await client.call_tool("get_frames", {"recording_id": "controlled", "t0": 0, "t1": 2, "max_frames": 2})
                assert not frames.is_error
                assert frames.structured_content["timestamps_s"] == [0.5, 1.5]
                assert sum(block.type == "image" for block in frames.content) == 2
                transcript = await client.call_tool("get_transcript", {"recording_id": "controlled", "t0": 0, "t1": 2})
                assert transcript.structured_content["status"] == "no_audio"
                moments = await client.call_tool("find_moment", {"recording_id": "controlled", "query": "red screen"})
                assert len(moments.structured_content["matches"]) == 5
                text = await client.call_tool("get_screen_text", {"recording_id": "controlled", "t0": 0, "t1": 1})
                assert text.structured_content["frames"][0]["text"] == "Controlled"
                invalid = await client.call_tool("get_recording", {"recording_id": "../../.env"})
                assert invalid.is_error
                resources = await client.list_resources()
                assert {str(resource.uri) for resource in resources.resources} == {"svh://recordings", "svh://provenance"}
                data = await client.read_resource("svh://recordings")
                assert "path" not in json.loads(data.contents[0].text)[0]
                prompts = await client.list_prompts()
                assert "inspect_recording_v1" in {prompt.name for prompt in prompts.prompts}
                prompt = await client.get_prompt("inspect_recording_v1", {"recording_id": "controlled", "question": "What is shown?"})
                assert "untrusted" in prompt.messages[0].content.text
                adapted = await harness_tools(client)
                frame_tool = next(tool for tool in adapted if tool.name == "get_frames")
                frame_reply = await frame_tool.ainvoke({"type": "tool_call", "id": "frame-call",
                    "name": "get_frames", "args": {"recording_id": "controlled", "t0": 0, "t1": 2, "max_frames": 1}})
                assert frame_reply.artifact["timestamps_s"] == [1.0]
                assert any(item.get("type") == "image_url" and item["image_url"]["url"].startswith("data:image/png;base64,")
                           for item in frame_reply.content)
                with tracing_context(enabled=False):
                    agent = create_deep_agent(model=OneToolModel(), tools=adapted, subagents=[])
                    result = await agent.ainvoke({"messages": [{"role": "user", "content": "Read the registered metadata."}]},
                                                config={"recursion_limit": 8})
                replies = [message for message in result["messages"] if isinstance(message, ToolMessage)]
                assert len(replies) == 1 and replies[0].status == "success"
                assert replies[0].artifact["id"] == "controlled"
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, timeout=10)
            sock.close()

    asyncio.run(run())
