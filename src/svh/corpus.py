"""Bind annotated temporal evidence to revalidated fail-before/pass-after runs.

This is M0 curation, not ingestion or automated claim extraction. No caller-
supplied `verified` Boolean is trusted: source bytes and raw logs are rechecked.
"""

import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from svh.native import evaluation_script, evidence, verified_pair
from svh.oracle import contained, wilson
from svh.sources import DATASET, REVISION, rows


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path):
    data = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration,format_name:stream=codec_type,nb_frames",
        "-of", "json", str(path),
    ], timeout=30))
    duration = float(data["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Media must have a positive finite duration")
    return {"duration_s": duration,
            "has_audio": any(stream["codec_type"] == "audio" for stream in data["streams"]),
            "kind": "animated_image" if data["format"]["format_name"] == "gif" else "video"}


def checked_file(root, relative, expected):
    path = contained(root, relative)
    if digest(path) != expected:
        raise ValueError(f"Hash mismatch: {relative}")
    return path


def freeze_proof(root, report_path):
    """Retain byte-identical logs and a content-addressed proof before admission."""
    report = json.loads(report_path.read_text())
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", report["task"]):
        raise ValueError("Unsafe task identifier in proof")
    source_hash = digest(report_path)
    destination = contained(root, "data/external/proofs/" + source_hash)
    destination.mkdir(parents=True, exist_ok=True)
    for side in ["pre", "post"]:
        source = contained(root, str(Path(report["raw_logs"]) / (side + ".log")))
        if digest(source) != report["results"][side]["raw_log_sha256"]:
            raise ValueError("Cannot freeze changed execution logs")
        target = destination / source.name
        if target.exists() and digest(target) != digest(source):
            raise ValueError("Content-addressed proof was modified")
        if not target.exists():
            shutil.copyfile(source, target)
    report["raw_logs"] = str(destination.relative_to(root))
    report["source_report_sha256"] = source_hash
    payload = json.dumps(report, indent=2) + "\n"
    path = root / "notes/runs/proofs" / (report["task"] + "-" + hashlib.sha256(payload.encode()).hexdigest()[:16] + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text() != payload:
        raise ValueError("Content-addressed report was modified")
    path.write_text(payload)
    return path


def validate_external(root: Path, annotation: Path, *, pinned_rows=None):
    data = json.loads(annotation.read_text())
    schema = json.loads((root / "evals/schema/external.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
    if data["source"]["dataset"] != DATASET or data["source"]["revision"] != REVISION:
        raise ValueError("Unrecognized dataset revision")
    external = root / "data/external"
    row_path = checked_file(root, data["source"]["row_path"], data["source"]["row_sha256"])
    if not row_path.is_relative_to(external.resolve()):
        raise ValueError("Raw source rows must stay in the ignored source directory")
    row = json.loads(row_path.read_text())
    task = data["source"]["instance_id"]
    if pinned_rows is None:
        pinned_rows = {item["instance_id"]: item for item in rows(external / "swebench-multimodal")}
    if row != pinned_rows.get(task):
        raise ValueError("Source row differs from pinned release")
    app = data["app"]
    if (app["repo"] != row["repo"] or app["base_commit"] != row["base_commit"]
            or app["fix_patch_sha256"] != hashlib.sha256(row["patch"].encode()).hexdigest()
            or app["test_patch_sha256"] != hashlib.sha256(row["test_patch"].encode()).hexdigest()):
        raise ValueError("Annotation's source states differ from the executed task")
    if app["image"].split("@")[0] != row["image"].removesuffix(":latest"):
        raise ValueError("Image repository does not match the source task")
    media = data["media"]
    source_urls = set(re.findall(r'https?://[^\s<>"\]\)]+', row["problem_statement"] + "\n" + json.dumps(row["image_assets"])))
    if media["source_url"] not in source_urls:
        raise ValueError("Media URL is not attached to the pinned issue")
    path = checked_file(root, media["path"], media["sha256"])
    if not path.is_relative_to(external.resolve()):
        raise ValueError("External media must remain reference-only under the ignored directory")
    actual = probe(path)
    if (not math.isfinite(media["duration_s"]) or not math.isfinite(data["review"]["interval_s"])
            or abs(actual["duration_s"] - media["duration_s"]) > 0.05
            or actual["has_audio"] != media["has_audio"] or actual["kind"] != media["kind"]):
        raise ValueError("Annotation disagrees with decoded media metadata")
    seen = set()
    expected = set()
    for claim in data["claims"]:
        start, end = claim["t_start_s"], claim["t_end_s"]
        if not math.isfinite(start) or not math.isfinite(end) or not 0 <= start < end <= actual["duration_s"]:
            raise ValueError("Claim timestamps fall outside decoded media")
        if claim["id"] in seen:
            raise ValueError("Duplicate claim ID")
        seen.add(claim["id"])
        expected.update(claim["expected_tests"])
    if expected != set(row["FAIL_TO_PASS"]):
        raise ValueError("Annotated claims must cover exactly the executed target tests")
    reviews = json.loads((root / "evals/reviews.json").read_text())
    review = reviews["cases"].get(task, {})
    if review.get("oracle_alignment") != "direct":
        raise ValueError("Manual review does not establish direct oracle-to-claim alignment")
    if review.get("media_sha256") != media["sha256"]:
        raise ValueError("Manual review is for different media bytes")
    observed_claims = [{key: claim[key] for key in ("t_start_s", "t_end_s", "text")} for claim in data["claims"]]
    reviewed_claims = review.get("claims")
    if reviewed_claims is None:
        reviewed_claims = [{key: review[key] for key in ("t_start_s", "t_end_s", "text")}]
    if observed_claims != reviewed_claims:
        raise ValueError("Annotation claims differ from the manually reviewed claims")
    oracle = data["oracle"]
    report_path = checked_file(root, oracle["report_path"], oracle["report_sha256"])
    report = json.loads(report_path.read_text())
    if (report["task"] != task or report["row_sha256"] != data["source"]["row_sha256"]
            or report["base_commit"] != app["base_commit"] or report["image"] != app["image"]
            or report["fix_patch_sha256"] != app["fix_patch_sha256"]
            or report["test_patch_sha256"] != app["test_patch_sha256"]):
        raise ValueError("Oracle proof does not match annotated source states")
    if (report["upstream_eval_sha256"] != hashlib.sha256(row["eval_script"].encode()).hexdigest()
            or report["executed_eval_sha256"] != hashlib.sha256(evaluation_script(row).encode()).hexdigest()):
        raise ValueError("Executed test script differs from the reviewed source contract")
    results = {}
    for side in ["pre", "post"]:
        log_path = contained(root, str(Path(report["raw_logs"]) / (side + ".log")))
        previous = report["results"][side]
        if digest(log_path) != previous["raw_log_sha256"]:
            raise ValueError("Oracle raw log changed after execution")
        results[side] = {"docker_exit_code": previous["docker_exit_code"], "timeout": previous["timeout"],
                         **evidence(log_path.read_text(errors="replace"), row["FAIL_TO_PASS"])}
    if not verified_pair(results["pre"], results["post"], app["base_commit"]):
        raise ValueError("Raw execution evidence does not verify the annotated case")
    return data


def corpus_gate(root, paths):
    pinned = {row["instance_id"]: row for row in rows(root / "data/external/swebench-multimodal")}
    outcomes = []
    identities = set()
    media_hashes = set()
    for path in paths:
        try:
            item = validate_external(root, path, pinned_rows=pinned)
            identity = item["source"]["instance_id"]
            if identity in identities:
                raise ValueError("Duplicate source task in evaluation set")
            if item["media"]["sha256"] in media_hashes:
                raise ValueError("Duplicate temporal artifact in evaluation set")
            identities.add(identity)
            media_hashes.add(item["media"]["sha256"])
            outcomes.append({"annotation": str(path.relative_to(root)), "id": item["id"], "accepted": True})
        except (ValueError, KeyError, OSError, ValidationError, subprocess.SubprocessError) as error:
            outcomes.append({"annotation": str(path.relative_to(root)), "accepted": False, "reason": str(error)})
    accepted = sum(item["accepted"] for item in outcomes)
    interval = wilson(accepted, len(outcomes))
    return {"cases": outcomes, "accepted": accepted, "total": len(outcomes),
            "wilson_95": interval, "required_wilson_lower": 0.7,
            "passed": 10 <= len(outcomes) <= 20 and accepted == len(outcomes) and interval[0] >= 0.7,
            "scope": "Curated visual-only supplied-oracle gate; speech and generated-reproduction gates remain separate"}
