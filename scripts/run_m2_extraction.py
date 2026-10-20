"""Sequential matched-condition M2 attempts, retaining every frozen case."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path

from svh.evidence import Evidence
from svh.extract import public_tasks, extract_claims, PROMPT
from svh.gemini import configured_model

parser = argparse.ArgumentParser()
parser.add_argument("--corpus", type=Path, default=Path("evals/frozen-m0.json"))
parser.add_argument("--only")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
runtime = root / "data/runtime/m2"
runtime.mkdir(parents=True, exist_ok=True)
lock = (runtime / "extraction.lock").open("a")
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
corpus_sha, tasks = public_tasks(root, args.corpus)
if args.only and args.only not in {task["id"] for task in tasks}:
    raise SystemExit("Unknown frozen recording identifier")
evidence = Evidence.from_corpus(root, args.corpus)
rubric_path = root / "evals/m2-rubric.json"
rubric_sha = hashlib.sha256(rubric_path.read_bytes()).hexdigest()
model = configured_model(root, output_cap=4096)
for condition in ("issue-only", "issue+media"):
    output = runtime / (condition + ".json")
    if output.exists():
        report = json.loads(output.read_text())
        if report["corpus_sha256"] != corpus_sha or report["rubric_sha256"] != rubric_sha:
            raise SystemExit("M2 attempt report belongs to different frozen inputs")
        for prior in report["cases"]:
            if prior["status"] == "completed" and (prior["identity"]["prompt_sha256"] != hashlib.sha256(PROMPT.encode()).hexdigest()
                    or prior["identity"]["model"] != model.model):
                raise SystemExit("Do not mix extraction prompts or models in a matched run")
    else:
        report = {"corpus_sha256": corpus_sha, "rubric_sha256": rubric_sha, "condition": condition,
                  "cases": [{"id": task["id"], "status": "not_attempted", "predictions": []} for task in tasks]}
    for task, attempt in zip(tasks, report["cases"], strict=True):
        if attempt["id"] != task["id"]:
            raise SystemExit("M2 case ordering changed")
        if (args.only and task["id"] != args.only) or attempt["status"] != "not_attempted":
            continue
        print(condition + " " + task["id"], flush=True)
        try:
            result = extract_claims(evidence, task, condition, model,
                                   runtime / condition / (task["id"] + ".response.json"))
        except Exception as error:
            result = {"id": task["id"], "status": "error", "error_type": type(error).__name__,
                      "predictions": [], "questions": [], "abstain_reason": "Extraction failed; raw response retained when available"}
        attempt.clear()
        attempt.update(result)
        report["budget"] = model._budget.summary()
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(report, indent=2) + "\n")
        temporary.replace(output)
        print(json.dumps({"id": task["id"], "status": result["status"],
                          "predictions": len(result["predictions"]), "budget": report["budget"]}), flush=True)
