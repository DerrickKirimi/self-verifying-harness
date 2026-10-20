"""Freeze canonical refined claims without editing any model-generated values."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--checkpoints", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--allow-partial", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
data = (root / args.checkpoints).read_bytes()
checkpoints = json.loads(data)
if not args.allow_partial and any(case["status"] == "not_attempted" for case in checkpoints["cases"]):
    raise SystemExit("Checkpoint run is incomplete; do not freeze a reduced denominator")
report = {"corpus_sha256": checkpoints["corpus_sha256"], "condition": checkpoints["condition"],
          "origin_extraction_sha256": checkpoints["extraction_sha256"],
          "checkpoint_sha256": hashlib.sha256(data).hexdigest(),
          "checkpoint_model": checkpoints["model"], "budget": checkpoints["budget"], "cases": []}
for case in checkpoints["cases"]:
    report["cases"].append({"id": case["id"], "status": case["status"],
        "predictions": case.get("refined_predictions", []), "questions": case.get("questions", []),
        "response_sha256": case.get("trace_sha256"),
        "abstain_reason": case.get("reason"), "source_unchanged": case.get("source_unchanged")})
destination = root / args.output
destination.parent.mkdir(parents=True, exist_ok=True)
if destination.exists() and destination.read_text() != json.dumps(report, indent=2) + "\n":
    raise SystemExit("Refuse to overwrite a different frozen prediction artifact")
destination.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"condition": report["condition"], "cases": len(report["cases"]),
                  "completed": sum(case["status"] == "completed" for case in report["cases"])}))
