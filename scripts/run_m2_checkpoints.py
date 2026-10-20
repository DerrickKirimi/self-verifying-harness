"""Existing-harness code checkpoints; no source fix or reproduction yet."""
import argparse
import asyncio
import fcntl
import hashlib
import json
import re
from pathlib import Path

from svh.checkpoint import inspect_code, checkpoint_prompt
from svh.docker_backend import sandbox
from svh.extract import public_tasks
from svh.gemini import configured_model
from svh.mcp_process import evidence_client

parser = argparse.ArgumentParser()
parser.add_argument("--corpus", type=Path, default=Path("evals/frozen-m0.json"))
parser.add_argument("--only")
parser.add_argument("--condition", choices=["both", "issue-only", "issue+media"], default="both")
parser.add_argument("--model", choices=["gemini-3.5-flash-lite", "gemini-3.8-flash"], default="gemini-3.8-flash")
parser.add_argument("--max-steps", type=int, default=30)
parser.add_argument("--run-name", required=True)
args = parser.parse_args()
if not re.fullmatch(r"[A-Za-z0-9_-]{1,64}", args.run_name):
    raise SystemExit("Use a simple non-secret run name")
root = Path(__file__).resolve().parents[1]
runtime = root / "data/runtime/m2"
runtime.mkdir(parents=True, exist_ok=True)
checkpoint_root = runtime / ("checkpoints-" + args.run_name)
checkpoint_root.mkdir(parents=True, exist_ok=True)
lock = (runtime / "checkpoint.lock").open("a")
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
corpus_sha, tasks = public_tasks(root, args.corpus)
if args.only and args.only not in {task["id"] for task in tasks}:
    raise SystemExit("Unknown frozen recording identifier")
if not 8 <= args.max_steps <= 80:
    raise SystemExit("Checkpoint step cap must be between 8 and 80")
model = configured_model(root, name=args.model, output_cap=4096)
model.reasoning_effort = "low"


async def run():
    async with evidence_client(root, args.corpus, checkpoint_root / "mcp.log") as client:
        for condition in ("issue-only", "issue+media"):
            if args.condition != "both" and condition != args.condition:
                continue
            extraction_path = runtime / (condition + ".json")
            extraction = json.loads(extraction_path.read_text())
            extraction_sha = hashlib.sha256(extraction_path.read_bytes()).hexdigest()
            if extraction["corpus_sha256"] != corpus_sha:
                raise ValueError("Claims belong to a different corpus")
            output = checkpoint_root / (condition + ".json")
            report = json.loads(output.read_text()) if output.exists() else {
                "corpus_sha256": corpus_sha, "extraction_sha256": extraction_sha, "condition": condition,
                "checkpoint_prompt_sha256": hashlib.sha256(checkpoint_prompt(condition).encode()).hexdigest(),
                "model": args.model, "thinking_level": "low", "step_cap": args.max_steps,
                "cases": [{"id": task["id"], "status": "not_attempted"} for task in tasks]}
            if (report["corpus_sha256"] != corpus_sha or report["extraction_sha256"] != extraction_sha
                    or report.get("checkpoint_prompt_sha256") != hashlib.sha256(checkpoint_prompt(condition).encode()).hexdigest()
                    or report.get("model") != args.model or report.get("step_cap") != args.max_steps):
                raise ValueError("Do not mix checkpoints from different claim outputs")
            for task, claims, attempt in zip(tasks, extraction["cases"], report["cases"], strict=True):
                if task["id"] != claims["id"] or task["id"] != attempt["id"]:
                    raise ValueError("Frozen checkpoint ordering changed")
                if (args.only and args.only != task["id"]) or attempt["status"] != "not_attempted":
                    continue
                if claims["status"] == "not_attempted":
                    continue
                print(condition + " code checkpoint " + task["id"], flush=True)
                if not claims["predictions"]:
                    result = {"id": task["id"], "status": "abstained", "reason": "No extracted claim to inspect"}
                else:
                    try:
                        with sandbox(task["image"], task["base_commit"]) as backend:
                            result = await inspect_code(task, claims, model, backend, client,
                                checkpoint_root / ("traces-" + condition) / (task["id"] + ".json"), condition=condition, max_steps=args.max_steps)
                    except Exception as error:
                        result = {"id": task["id"], "status": "error", "error_type": type(error).__name__,
                                  "reason": "Checkpoint failed; inspect retained local trace/log"}
                attempt.clear()
                attempt.update(result)
                report["budget"] = model._budget.summary()
                temporary = output.with_suffix(".tmp")
                temporary.write_text(json.dumps(report, indent=2) + "\n")
                temporary.replace(output)
                print(json.dumps({"id": task["id"], "status": result["status"], "budget": report["budget"]}), flush=True)


asyncio.run(run())
