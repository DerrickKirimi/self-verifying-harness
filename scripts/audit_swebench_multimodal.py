"""Audit pinned local Parquet data without executing any dataset-provided code.

Run with `uv run --extra datasets python -I scripts/audit_swebench_multimodal.py`.
Gold patches stay in the ignored source directory, never in the candidate report.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

import pyarrow.parquet as pq


REVISION = "4e6662d51c48e475f7f346e4fa09a6f8b31fcaa5"
EXPECTED = {
    "dev-00000-of-00001.parquet": "714f4b815680608168d620c87c6b3420b3d4690d6656fc85b1da6511bfb55931",
    "test-00000-of-00001.parquet": "ce21141e0b2aadb6b91cf21d27c93e4c159afb1c4c25b7b4ea9222d823dd9da7",
}
URL = re.compile(r'https?://[^\s<>"\]\)]+')
VIDEO = {".mp4", ".webm", ".mov", ".m4v"}


def asset_urls(row):
    assets = row.get("image_assets") or {}
    if isinstance(assets, str):
        assets = json.loads(assets)
    urls = list(URL.findall(row.get("problem_statement") or ""))
    for asset in assets.get("problem_statement", []):
        urls.append(asset["url"] if isinstance(asset, dict) else asset)
    return sorted(set(url.rstrip(".,") for url in urls))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("data/external/swebench-multimodal"))
    parser.add_argument("--output", type=Path, default=Path("notes/runs/swebench-multimodal-audit.json"))
    parser.add_argument("--export-pilot", action="store_true", help="export the inspected BPMN row, including gold patches, only into the ignored source directory")
    args = parser.parse_args()
    ignored_root = Path(__file__).resolve().parents[1] / "data/external"
    if args.export_pilot and not args.source.resolve().is_relative_to(ignored_root):
        raise ValueError("Gold-patch exports must stay under the gitignored data/external directory")
    counts = {}
    candidates = []
    sources = []
    pilot_row = None
    for path in sorted((args.source / "data").glob("*.parquet")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != EXPECTED.get(path.name):
            raise ValueError(f"Source does not match pinned revision: {path}")
        split = path.name.split("-")[0]
        rows = pq.read_table(path).to_pylist()
        counts[split] = counts.get(split, 0) + len(rows)
        sources.append({"file": str(path.relative_to(args.source)),
                        "sha256": digest, "rows": len(rows)})
        for row in rows:
            if row["instance_id"] == "bpmn-io__bpmn-js-1655":
                pilot_row = row
            urls = asset_urls(row)
            videos = [url for url in urls if Path(urlsplit(url).path).suffix.lower() in VIDEO]
            gifs = [url for url in urls if Path(urlsplit(url).path).suffix.lower() == ".gif"]
            unresolved = [url for url in urls if "/assets/" in url and not Path(urlsplit(url).path).suffix]
            if videos or gifs or unresolved or "<video" in row.get("problem_statement", "").lower():
                candidates.append({
                    "id": row["instance_id"], "split": split, "repo": row["repo"],
                    "base_commit": row["base_commit"], "image": row.get("image"),
                    "video_urls": videos, "gif_urls": gifs, "unresolved_asset_urls": unresolved,
                    "has_fix_patch": bool(row.get("patch")),
                    "has_test_patch": bool(row.get("test_patch")),
                    "has_eval_script": bool(row.get("eval_script")),
                    "eval_type": row.get("eval_type"),
                    "fail_to_pass_count": len(row.get("FAIL_TO_PASS") or []),
                    "pass_to_pass_count": len(row.get("PASS_TO_PASS") or []),
                })
    if set(counts) != {"dev", "test"}:
        raise ValueError("Both pinned dev and test Parquet files are required")
    if args.export_pilot:
        if pilot_row is None:
            raise ValueError("Pilot task missing from pinned source")
        destination = args.source / "bpmn-pilot-row.json"
        if destination.exists():
            if json.loads(destination.read_text()) != pilot_row:
                raise ValueError("Existing pilot row does not match pinned Parquet data")
        else:
            destination.write_text(json.dumps(pilot_row, indent=2) + "\n")
    report = {
        "dataset": "SWE-bench/SWE-bench_Multimodal", "revision": REVISION,
        "scope": "Issue-media URL inventory; extensions and untyped links are candidates, not decoded media",
        "rows_by_split": counts, "sources": sources,
        "video_candidate_tasks": sum(bool(row["video_urls"]) for row in candidates),
        "gif_candidate_tasks": sum(bool(row["gif_urls"]) for row in candidates),
        "unresolved_candidate_tasks": sum(bool(row["unresolved_asset_urls"]) for row in candidates),
        "candidates": candidates,
        "oracle_runs_performed_by_audit": 0,
        "pilot_row_matches_pinned_source": True if args.export_pilot else None,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key not in ("candidates", "sources")}, indent=2))
    print("Video candidate IDs:", [row["id"] for row in candidates if row["video_urls"]])


if __name__ == "__main__":
    main()
