"""Admit completed supplied oracles using explicit, manually recorded reviews.

Never marks unseen media reviewed or trusts a saved verification Boolean.
Run with the installed interpreter: uv run python -I scripts/admit_reviewed_cases.py.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from svh.corpus import digest, freeze_proof, validate_external
from svh.sources import DATASET, REVISION, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-proofs", action="store_true", help="bind annotations to newly executed proofs; retain all historical proof snapshots")
    args = parser.parse_args()
    root = Path.cwd().resolve()
    reviews = json.loads((root / "evals/reviews.json").read_text())
    inventory = json.loads((root / "notes/runs/m0-media-inventory.json").read_text())
    progress = json.loads((root / "notes/runs/m0-curation-progress.json").read_text())
    pinned = {row["instance_id"]: row for row in rows(root / "data/external/swebench-multimodal")}
    outcomes = []
    for task, review in reviews["cases"].items():
        path = root / "evals/annotations" / ("swebench-bpmn-" + task.rsplit("-", 1)[1] + ".json")
        if review.get("oracle_alignment") != "direct":
            if path.exists():
                raise ValueError("An excluded claim must not remain in the admission directory: " + task)
            outcomes.append({"task": task, "state": "not-admitted", "reason": review["oracle_alignment_reason"]})
            continue
        if path.exists() and not args.refresh_proofs:
            validate_external(root, path, pinned_rows=pinned)
            outcomes.append({"task": task, "state": "existing-validated"})
            continue
        state = progress["cases"].get(task, {})
        if state.get("state") != "oracle-passed":
            if path.exists() and args.refresh_proofs:
                raise ValueError("Cannot refresh an admitted case without a new passing oracle: " + task)
            outcomes.append({"task": task, "state": "not-admitted", "reason": state.get("state", "pending")})
            continue
        media = inventory[task]
        if (review["media_sha256"] != media["sha256"]
                or review["pages_viewed"] != len(media["sheets"])
                or review["screening"] != "no-sensitive-content-observed"):
            raise ValueError("Review does not cover the inventoried artifact: " + task)
        row_path = root / state["row"]
        row = json.loads(row_path.read_text())
        proof = freeze_proof(root, root / state["report"])
        report = json.loads(proof.read_text())
        annotation = {
            "format": "svh.external.v1", "id": path.stem,
            "source": {"dataset": DATASET, "revision": REVISION, "instance_id": task,
                       "row_path": state["row"], "row_sha256": digest(row_path)},
            "app": {"repo": row["repo"], "base_commit": row["base_commit"],
                    "fix_patch_sha256": hashlib.sha256(row["patch"].encode()).hexdigest(),
                    "test_patch_sha256": hashlib.sha256(row["test_patch"].encode()).hexdigest(),
                    "image": report["image"]},
            "media": {key: media[key] for key in
                      ["path", "sha256", "source_url", "duration_s", "has_audio", "kind"]},
            "review": {"method": "contact-sheet", "interval_s": review["interval_s"],
                       "screening": review["screening"], "distribution": "reference-only",
                       "reviewed_at": review.get("reviewed_at", reviews["reviewed_at"])},
            "claims": [{"id": "visual-claim", "t_start_s": review["t_start_s"],
                        "t_end_s": review["t_end_s"], "text": review["text"],
                        "evidence_mode": "shown", "expected_tests": row["FAIL_TO_PASS"]}],
            "oracle": {"runner": "swebench-karma", "report_path": str(proof.relative_to(root)),
                       "report_sha256": digest(proof)},
        }
        # Validate before publishing to the admission directory. A saved pass
        # flag alone never establishes an accepted case.
        temporary = root / "data/external/candidate-annotation.json"
        temporary.write_text(json.dumps(annotation, indent=2) + "\n")
        validate_external(root, temporary, pinned_rows=pinned)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.replace(path)
        outcomes.append({"task": task, "state": "admitted"})
    result = {"updated_at": datetime.now(timezone.utc).isoformat(), "cases": outcomes}
    (root / "notes/runs/m0-admission-progress.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
