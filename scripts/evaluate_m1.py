"""Measure frozen retrieval gates separately from model-visible ingestion."""
import hashlib
import json
from pathlib import Path

from svh.corpus import load_frozen_corpus
from svh.ingest import retrieve
from svh.oracle import wilson

root = Path(__file__).resolve().parents[1]
manifest, annotations = load_frozen_corpus(root, Path("evals/frozen-m0.json"))
results = {method: [] for method in ("fixed45", "temporal3", "midpoint")}
for annotation in annotations:
    path = root / "data/runtime/visual-index" / (annotation["id"] + ".json")
    index = json.loads(path.read_text()) if path.exists() else None
    if index and (index["identity"]["corpus_sha256"] != manifest["corpus_sha256"]
                  or index["identity"]["media_sha256"] != annotation["media"]["sha256"]):
        raise ValueError("Index belongs to different frozen evidence")
    claim = annotation["claims"][0]
    start, end = claim["t_start_s"], claim["t_end_s"]
    for method in results:
        hits = ([{"timestamp_s": annotation["media"]["duration_s"] / 2}] if method == "midpoint"
                else retrieve(index, claim["text"], method) if index else [])
        times = [hit["timestamp_s"] for hit in hits]
        distances = [max(start - time, time - end, 0) for time in times]
        results[method].append({"id": annotation["id"], "query": claim["text"],
            "gold_span": [start, end], "timestamps_s": times,
            "distance_s": distances, "hit1": bool(distances and distances[0] <= 5),
            "hit5": any(distance <= 5 for distance in distances),
            "strict1": bool(distances and distances[0] == 0),
            "strict5": any(distance == 0 for distance in distances),
            "index_sha256": hashlib.sha256(path.read_bytes()).hexdigest() if index else None})

summary = {}
for method, cases in results.items():
    summary[method] = {}
    for metric in ("hit1", "hit5", "strict1", "strict5"):
        successes = sum(case[metric] for case in cases)
        summary[method][metric] = {"successes": successes, "n": len(cases),
                                   "wilson95": wilson(successes, len(cases))}
# Complexity earns its place only with better strict localization and no gate loss.
selected = "fixed45"
if (summary["temporal3"]["strict1"]["successes"] > summary["fixed45"]["strict1"]["successes"]
    and all(summary["temporal3"][key]["successes"] >= summary["fixed45"][key]["successes"] for key in ("hit1", "hit5"))):
    selected = "temporal3"
metrics = summary[selected]
report = {"corpus_sha256": manifest["corpus_sha256"], "selected": selected,
          "passed": len(annotations) >= 10 and metrics["hit1"]["wilson95"][0] >= .5 and metrics["hit5"]["wilson95"][0] >= .7,
          "summary": summary, "cases": results,
          "limitations": ["Curated short clips, one application, silent media", "Gold claim text used only as evaluation query", "Common caption budget across methods"]}
(root / "notes/runs/m1-retrieval.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({key: value for key, value in report.items() if key != "cases"}, indent=2))
