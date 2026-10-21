"""Replay recording evidence and the frozen generated repair; no model calls."""
import argparse
import asyncio
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.request
import uuid

from svh.mcp_process import evidence_client
from svh.tasks import load_task

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "tasks/generated-v1/swebench-bpmn-1679"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


async def evidence(manifest, work, task):
    async with evidence_client(ROOT, None, work / "mcp.log", task_manifest=manifest) as client:
        metadata = await client.call_tool("get_recording", {"recording_id": task["id"]})
        frames = await client.call_tool("get_frames", {
            "recording_id": task["id"], "t0": 14.0, "t1": 18.9, "max_frames": 3})
        if metadata.is_error or frames.is_error:
            raise ValueError("MCP evidence retrieval failed; inspect the local MCP log")
        images = [block for block in frames.content if block.type == "image"]
        if len(images) != 3:
            raise ValueError("Expected three actual recording frames")
        paths = []
        for i, block in enumerate(images, 1):
            path = work / f"frame-{i}.png"
            content = base64.b64decode(block.data, validate=True)
            if block.mime_type != "image/png" or not content.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError("Expected a decoded PNG frame")
            path.write_bytes(content)
            paths.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path)})
        return paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-name", default="demo-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6])
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,48}", args.run_name):
        parser.error("Use a run name of 1–48 letters, digits, underscores or hyphens")
    if not (ROOT / "data/runtime/harbor-venv/bin/python").is_file():
        raise SystemExit("Install the isolated Harbor environment first; see README.md")
    subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, check=True)
    for tool in ("ffprobe", "ffmpeg"):
        subprocess.run([tool, "-version"], stdout=subprocess.DEVNULL, check=True)
    package = json.loads((TASK / "bundle.json").read_text())
    for name, expected in package["files"].items():
        if digest(TASK / name) != expected:
            raise ValueError("Frozen generated task package changed")
    proof = json.loads((TASK / "tests/proof.json").read_text())
    work = ROOT / "data/runtime/demos" / args.run_name
    if (ROOT / "notes/runs" / f"harbor-{args.run_name}.json").exists():
        raise SystemExit("Use a new run name to preserve prior observations")
    work.mkdir(parents=True, exist_ok=False)
    media = proof["media"]
    folder = ROOT / "data/external/demo-media" / media["sha256"]
    folder.mkdir(parents=True, exist_ok=True)
    recording = folder / "recording.gif"
    if not recording.exists():
        print("Downloading the reviewed public recording (hash verified)", flush=True)
        # This URL is part of the immutable, reviewed task; no arbitrary user URLs.
        if not media["source_url"].startswith("https://user-images.githubusercontent.com/"):
            raise ValueError("Unexpected demo media host")
        with urllib.request.urlopen(media["source_url"], timeout=60) as response:
            content = response.read(128 * 1024**2 + 1)
        if len(content) > 128 * 1024**2 or hashlib.sha256(content).hexdigest() != media["sha256"]:
            raise ValueError("Downloaded recording does not match the reviewed bytes")
        recording.write_bytes(content)
    if digest(recording) != media["sha256"]:
        raise ValueError("Cached recording changed")
    manifest = work / "task.json"
    manifest.write_text(json.dumps({
        "format": "svh.task.v1", "id": "demo-recording-1679",
        "problem_statement": (TASK / "instruction.md").read_text().split("\n\n")[1],
        "environment": {"adapter": "bpmn-karma-v1", "image": proof["pre"]["image"],
                        "base_commit": proof["pre"]["base_commit"]},
        "recording": {"path": str(recording), **media}}, indent=2) + "\n")
    identity, task, _ = load_task(ROOT, manifest)
    print("Retrieving three recording frames through authenticated MCP", flush=True)
    frames = asyncio.run(evidence(manifest, work, task))
    subprocess.run([sys.executable, "-I", str(ROOT / "scripts/install_buildx.py")], check=True)
    print("Replaying the frozen generated repair in actual Harbor Docker trials", flush=True)
    subprocess.run([sys.executable, "-I", str(ROOT / "scripts/run_harbor_integrity.py"),
                    "--task", str(TASK), "--run-name", args.run_name], check=True)
    integrity_path = ROOT / "notes/runs" / f"harbor-{args.run_name}.json"
    integrity = json.loads(integrity_path.read_text())
    if not integrity["passed"]:
        raise ValueError("Harbor integrity did not pass")
    result = {"format": "svh.demo.v1", "passed": True,
              "scope": "Recording MCP retrieval and frozen generated-repair replay; no fresh model generation",
              "model_calls": 0, "manifest_sha256": identity,
              "frames": frames, "harbor_report": str(integrity_path.relative_to(ROOT)),
              "harbor_report_sha256": digest(integrity_path)}
    report = work / "result.json"
    report.write_text(json.dumps(result, indent=2) + "\n")
    print(f"PASS: recording frames retrieved; original assertion fails; generated repair and regressions pass.\nResults and PNG frames: {work}\nHarbor report: {integrity_path}", flush=True)


if __name__ == "__main__":
    main()
