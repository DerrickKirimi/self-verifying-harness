"""Build local vectors without evaluation queries or additional API spending."""
import hashlib
import argparse
from importlib.metadata import version
import json
from pathlib import Path

from svh.evidence import Evidence
from svh.semantic import MODEL, REVISION, build, file_sha

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--corpus", type=Path, default=Path("evals/frozen-m0.json"))
args = parser.parse_args()
evidence = Evidence.from_corpus(root, args.corpus)
directory = root / "data/external/embeddinggemma-2" / REVISION
files = {str(path.relative_to(directory)): file_sha(path)
         for path in directory.rglob("*") if path.is_file() and ".cache" not in path.parts}
if "model.safetensors" not in files:
    raise SystemExit("Pinned safe model weights are not yet present")
report = {"model": MODEL, "revision": REVISION, "device": "cpu", "mode": "text-only",
          "files": files, "corpus_sha256": evidence.corpus_sha256,
          "versions": {name: version(name) for name in ("torch", "transformers", "sentence-transformers")},
          "cases": []}
for identifier in evidence.recordings:
    print("Embedding " + identifier, flush=True)
    manifest = build(root, root / "data/runtime/visual-index" / (identifier + ".json"),
                     root / "data/runtime/semantic-index" / (identifier + ".npy"))
    report["cases"].append({"id": identifier, "vectors_sha256": manifest["vectors_sha256"]})
    (root / "notes/runs/m1-semantic-index.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"cases": len(report["cases"]), "versions": report["versions"]}), flush=True)
