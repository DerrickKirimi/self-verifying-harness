"""Publish only the measured server-side method, without importing gold into MCP."""
import hashlib
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--corpus", type=Path, default=Path("evals/frozen-m0.json"))
parser.add_argument("--report", type=Path, default=Path("notes/runs/m1-selected-retrieval.json"))
args = parser.parse_args()
path = root / args.report
report = json.loads(path.read_text())
frozen = json.loads((root / args.corpus).read_text())
method = report["selected"]
metrics = report["summary"][method]
if (not report["passed"] or report["corpus_sha256"] != frozen["corpus_sha256"]
        or metrics["hit1"]["n"] != len(frozen["annotations"]) or metrics["hit1"]["n"] < 10
        or metrics["hit1"]["wilson95"][0] < .5 or metrics["hit5"]["wilson95"][0] < .7):
    raise SystemExit("Selected retrieval result does not meet the frozen gate")
policy = {"method": method, "corpus_sha256": report["corpus_sha256"],
          "measured_report_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
destination = root / "data/runtime/retrieval-policy.json"
destination.parent.mkdir(parents=True, exist_ok=True)
destination.write_text(json.dumps(policy, indent=2) + "\n")
print(json.dumps(policy, indent=2))
