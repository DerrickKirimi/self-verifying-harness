"""Pinned public-source readers. Reading task data never executes its code."""

import hashlib
import json
from pathlib import Path
import re
import subprocess


DATASET = "SWE-bench/SWE-bench_Multimodal"
REVISION = "4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5"
FILES = {
    "dev-00000-of-00001.parquet": "714f4b815680608168d620c87c6b3420b3d4690d6656fc85b1da6511bfb55931",
    "test-00000-of-00001.parquet": "ce21141e0b2aadb6b91cf21d27c93e4c159afb1c4c25b7b4ea9222d823dd9da7",
}


def rows(source: Path):
    import pyarrow.parquet as pq

    for name, expected in FILES.items():
        path = source / "data" / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Unrecognized dataset content: {path}")
        yield from pq.read_table(path).to_pylist()


def export_rows(source, ids):
    selected = {row["instance_id"]: row for row in rows(source) if row["instance_id"] in ids}
    if set(selected) != set(ids):
        raise ValueError("Selected task missing from pinned dataset")
    target = source / "cases"
    target.mkdir(exist_ok=True)
    for task, row in selected.items():
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", task):
            raise ValueError("Unsafe task ID")
        (target / (task + ".json")).write_text(json.dumps(row, indent=2) + "\n")
    return selected


def resolve_image(tag):
    if not re.fullmatch(r"swebench/[a-z0-9._-]+:latest", tag):
        raise ValueError("Expected an upstream swebench image tag")
    manifest = json.loads(subprocess.check_output(["docker", "manifest", "inspect", tag], timeout=90))
    candidates = [item for item in manifest.get("manifests", [])
                  if item.get("platform", {}).get("architecture") == "amd64"
                  and item.get("platform", {}).get("os") == "linux"]
    if len(candidates) != 1:
        raise ValueError("Expected exactly one Linux amd64 manifest")
    digest = candidates[0]["digest"]
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", digest):
        raise ValueError("Invalid image digest")
    return tag.removesuffix(":latest") + "@" + digest
