"""Recompute claim rates from frozen outputs and explicit review judgments."""
import argparse
import hashlib
import json
from pathlib import Path

from svh.claims import score
from svh.corpus import load_frozen_corpus

parser = argparse.ArgumentParser()
parser.add_argument("--predictions", type=Path, required=True)
parser.add_argument("--judgments", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--corpus", type=Path, default=Path("evals/frozen-m0.json"))
parser.add_argument("--checkpoints", type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
manifest, annotations = load_frozen_corpus(root, args.corpus)
data = (root / args.predictions).read_bytes()
predictions = json.loads(data)
judgments = json.loads((root / args.judgments).read_text())
rubric = json.loads((root / "evals/m2-rubric.json").read_text())
if manifest["corpus_sha256"] != rubric["corpus_sha256"]:
    raise SystemExit("Scoring rubric belongs to a different frozen corpus")
digest = hashlib.sha256(data).hexdigest()
result = score(predictions, judgments, annotations, rubric, digest)
result.update({"prediction_sha256": digest, "scorer": judgments.get("scorer", "unspecified"),
               "corpus_sha256": manifest["corpus_sha256"], "code_checkpoint_passed": False})
if args.checkpoints:
    checkpoint_data = (root / args.checkpoints).read_bytes()
    checkpoint = json.loads(checkpoint_data)
    if (checkpoint["corpus_sha256"] != manifest["corpus_sha256"]
            or checkpoint["extraction_sha256"] != predictions.get("origin_extraction_sha256", digest)):
        raise SystemExit("Checkpoints belong to a different extraction")
    if predictions.get("checkpoint_sha256") and predictions["checkpoint_sha256"] != hashlib.sha256(checkpoint_data).hexdigest():
        raise SystemExit("Refined predictions belong to different checkpoints")
    rows = {case["id"]: case for case in checkpoint["cases"]}
    result["code_checkpoint_passed"] = set(rows) == {case["id"] for case in predictions["cases"]} and all(
        not case["predictions"] or (rows[case["id"]]["status"] == "completed" and rows[case["id"]]["source_unchanged"])
        for case in predictions["cases"])
result["m2_gate_passed"] = result["claim_gate_passed"] and result["code_checkpoint_passed"]
(root / args.output).write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
