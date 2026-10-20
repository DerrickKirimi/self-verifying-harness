"""Exercise the real CLI/server against frozen public media, without models."""

import asyncio
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import socket
import subprocess
import sys

import httpx2

from svh.mcp_client import connect
from svh.mcp_server import private_token


async def main():
    root = Path.cwd().resolve()
    runtime = root / "data/runtime"
    runtime.mkdir(parents=True, exist_ok=True, mode=0o700)
    token = private_token(runtime / "mcp.token")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}/mcp"
    env = {key: os.environ[key] for key in ("PATH", "LANG", "LC_ALL") if key in os.environ}
    with (runtime / "mcp-smoke-server.log").open("w") as log:
        process = subprocess.Popen([sys.executable, "-I", "-m", "svh.cli", "mcp", "--port", str(port)],
                                   cwd=root, env=env, stdout=log, stderr=subprocess.STDOUT)
    try:
        async with httpx2.AsyncClient(timeout=2) as raw:
            async with asyncio.timeout(150):
                while True:
                    if process.poll() is not None:
                        raise RuntimeError("MCP CLI stopped during startup; inspect the private server log")
                    try:
                        response = await raw.get(url)
                        if response.status_code == 401:
                            break
                    except httpx2.TransportError:
                        pass
                    await asyncio.sleep(0.2)
        async with connect(url, token) as client:
            assert client.protocol_version == "2026-07-28"
            metadata = await client.call_tool("get_recording", {"recording_id": "swebench-bpmn-1655"})
            assert not metadata.is_error
            assert "path" not in metadata.structured_content
            frames = await client.call_tool("get_frames", {"recording_id": "swebench-bpmn-1655",
                "t0": 5, "t1": 6.8, "max_frames": 2})
            assert not frames.is_error
            images = [block for block in frames.content if block.type == "image"]
            assert len(images) == 2 and all(block.mime_type == "image/png" for block in images)
            transcript = await client.call_tool("get_transcript", {"recording_id": "swebench-bpmn-1655", "t0": 0, "t1": 6.8})
            assert transcript.structured_content["status"] == "no_audio"
            moments = await client.call_tool("find_moment", {"recording_id": "swebench-bpmn-1655", "query": "orange label"})
            assert not moments.is_error and moments.structured_content["matches"]
            screen = await client.call_tool("get_screen_text", {"recording_id": "swebench-bpmn-1655", "t0": 5, "t1": 6.8})
            assert not screen.is_error and screen.structured_content["frames"]
            resource = await client.read_resource("svh://provenance")
            provenance = json.loads(resource.contents[0].text)
            frozen = json.loads((root / "evals/frozen-m0.json").read_text())
            assert provenance["corpus_sha256"] == frozen["corpus_sha256"]
            tools = [tool.name for tool in (await client.list_tools()).tools]
            resources = [str(item.uri) for item in (await client.list_resources()).resources]
            prompts = [item.name for item in (await client.list_prompts()).prompts]
            report = {"run_at": datetime.now(timezone.utc).isoformat(), "passed": True,
                "scope": "Actual MCP CLI + HTTP SDK + frozen public media/index; no live model inference or retrieval quality claim",
                "retrieval_timestamps_s": [match["timestamp_s"] for match in moments.structured_content["matches"]],
                "screen_text_samples": len(screen.structured_content["frames"]),
                "versions": {name: version(name) for name in ("mcp", "deepagents", "langchain-google-genai")},
                "protocol_version": client.protocol_version, "unauthorized_status": response.status_code,
                "provenance": provenance, "tools": tools, "resources": resources, "prompts": prompts,
                "recording_id": metadata.structured_content["id"],
                "frame_timestamps_s": frames.structured_content["timestamps_s"],
                "frame_mime_types": [block.mime_type for block in images],
                "frame_base64_sizes": [len(block.data) for block in images],
                "transcript_status": transcript.structured_content["status"]}
            (root / "notes/runs/mcp-http-smoke.json").write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report, indent=2))
    finally:
        process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


if __name__ == "__main__":
    asyncio.run(main())
