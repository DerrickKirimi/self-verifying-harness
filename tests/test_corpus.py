"""Admission requires media, source and observed execution to stay bound together."""

import hashlib
import copy
import json
from pathlib import Path

import pytest

from svh.corpus import digest, freeze_corpus, load_frozen_corpus, validate_external
from svh.native import evaluation_script
from svh.sources import DATASET, REVISION


def hash_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


@pytest.fixture
def case(tmp_path, monkeypatch):
    repo = Path(__file__).resolve().parents[1]
    schema = tmp_path / "evals/schema/external.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_bytes((repo / "evals/schema/external.schema.json").read_bytes())
    source = tmp_path / "data/external/case"
    source.mkdir(parents=True)
    row = {"instance_id": "test-task", "repo": "bpmn-io/bpmn-js", "base_commit": "a" * 40,
           "patch": "source-fix", "test_patch": "frozen-tests", "image": "swebench/test:latest",
           "problem_statement": "https://example.com/bug.gif", "image_assets": {},
           "FAIL_TO_PASS": ["color"],
           "eval_script": "git apply -v - <<'END'\ntest patch\nEND\nrun-tests\n: '>>>>> End Test Output'\n"}
    row_path = source / "row.json"
    row_path.write_text(json.dumps(row))
    media = source / "bug.gif"
    media.write_bytes(b"fixture-media")
    logs = {}
    prefix = "SVH_BASE_COMMIT:" + row["base_commit"] + "\n"
    logs["pre"] = prefix + "Chrome Headless 131.0.0.0 (Linux x86_64) color FAILED\nAssertionError: expected red to equal blue\nExecuted 2 of 3 (1 FAILED) (skipped 1)\nTOTAL: 1 FAILED, 1 SUCCESS\nSVH_TEST_EXIT_CODE:1\n"
    logs["post"] = prefix + "Executed 2 of 3 (skipped 1)\nTOTAL: 2 SUCCESS\nSVH_TEST_EXIT_CODE:0\n"
    for side, text in logs.items():
        (source / (side + ".log")).write_text(text)
    report = {"task": row["instance_id"], "row_sha256": digest(row_path), "base_commit": row["base_commit"],
              "image": "swebench/test@sha256:" + "1" * 64,
              "fix_patch_sha256": hash_text(row["patch"]), "test_patch_sha256": hash_text(row["test_patch"]),
              "upstream_eval_sha256": hash_text(row["eval_script"]),
              "executed_eval_sha256": hash_text(evaluation_script(row)),
              "verified": True, "raw_logs": "data/external/case",
              "results": {side: {"docker_exit_code": 0, "timeout": False, "raw_log_sha256": hash_text(text)}
                          for side, text in logs.items()}}
    report_path = tmp_path / "proof.json"
    report_path.write_text(json.dumps(report))
    annotation = {
        "format": "svh.external.v1", "id": "test-task",
        "source": {"dataset": DATASET, "revision": REVISION, "instance_id": row["instance_id"],
                   "row_path": "data/external/case/row.json", "row_sha256": digest(row_path)},
        "app": {"repo": row["repo"], **{key: report[key] for key in ["base_commit", "image", "fix_patch_sha256", "test_patch_sha256"]}},
        "media": {"path": "data/external/case/bug.gif", "sha256": digest(media), "source_url": row["problem_statement"],
                  "duration_s": 5.0, "has_audio": False, "kind": "animated_image"},
        "review": {"method": "contact-sheet", "interval_s": 0.5, "screening": "no-sensitive-content-observed",
                   "distribution": "reference-only", "reviewed_at": "2026-10-20T00:00:00Z"},
        "claims": [{"id": "color", "t_start_s": 1, "t_end_s": 4, "text": "Label uses the incorrect color",
                    "evidence_mode": "shown", "expected_tests": ["color"]}],
        "oracle": {"runner": "swebench-karma", "report_path": "proof.json", "report_sha256": digest(report_path)},
    }
    path = tmp_path / "annotation.json"
    manual_review = {"cases": {row["instance_id"]: {
        "oracle_alignment": "direct", "media_sha256": annotation["media"]["sha256"],
        **{key: annotation["claims"][0][key] for key in ("t_start_s", "t_end_s", "text")},
    }}}
    (tmp_path / "evals/reviews.json").write_text(json.dumps(manual_review))
    monkeypatch.setattr("svh.corpus.probe", lambda path: {"duration_s": 5.0, "has_audio": False, "kind": "animated_image"})
    return tmp_path, path, annotation, row, report, report_path


def validate(case):
    root, path, annotation, row, report, report_path = case
    report_path.write_text(json.dumps(report))
    annotation["oracle"]["report_sha256"] = digest(report_path)
    path.write_text(json.dumps(annotation))
    return validate_external(root, path, pinned_rows={row["instance_id"]: row})


def test_complete_bound_evidence_is_accepted(case):
    assert validate(case)["id"] == "test-task"


@pytest.mark.parametrize("mutation,message", [
    (lambda a, r: a["media"].update(sha256="0" * 64), "Hash mismatch"),
    (lambda a, r: a["media"].update(source_url="https://example.com/unrelated.gif"), "not attached"),
    (lambda a, r: a["claims"][0].update(t_end_s=6), "timestamps"),
    (lambda a, r: a["claims"][0].update(expected_tests=["unrelated"]), "target tests"),
    (lambda a, r: a["app"].update(fix_patch_sha256="0" * 64), "source states"),
    (lambda a, r: r.update(executed_eval_sha256="0" * 64), "test script"),
    (lambda a, r: r["results"]["pre"].update(raw_log_sha256="0" * 64), "raw log"),
])
def test_unbound_evidence_is_rejected(case, mutation, message):
    mutation(case[2], case[4])
    with pytest.raises(ValueError, match=message):
        validate(case)


def test_success_boolean_cannot_override_observed_failure(case):
    source = case[0] / "data/external/case"
    # Forge the public Boolean and replace the pre-run with an all-passing run.
    (source / "pre.log").write_bytes((source / "post.log").read_bytes())
    case[4]["results"]["pre"]["raw_log_sha256"] = digest(source / "pre.log")
    case[4]["verified"] = True
    with pytest.raises(ValueError, match="does not verify"):
        validate(case)


def test_supporting_invariant_cannot_verify_broader_recorded_claim(case):
    path = case[0] / "evals/reviews.json"
    review = json.loads(path.read_text())
    review["cases"][case[3]["instance_id"]]["oracle_alignment"] = "supporting-invariant"
    path.write_text(json.dumps(review))
    with pytest.raises(ValueError, match="oracle-to-claim alignment"):
        validate(case)


def test_changed_claim_cannot_reuse_a_manual_review(case):
    case[2]["claims"][0]["text"] = "A different requirement with the same source test"
    with pytest.raises(ValueError, match="manually reviewed claims"):
        validate(case)


def test_incomplete_corpus_cannot_be_frozen(case, monkeypatch):
    validate(case)
    monkeypatch.setattr("svh.corpus.rows", lambda source: iter([case[3]]))
    with pytest.raises(ValueError, match="admission gate"):
        freeze_corpus(case[0], [case[1]], Path("frozen.json"))
    assert not (case[0] / "frozen.json").exists()


@pytest.fixture
def admitted_corpus(case, monkeypatch):
    root, _, template, original_row, original_report, _ = case
    paths, pinned, reviews = [], [], {}
    folder = root / "evals/annotations"
    folder.mkdir()
    for index in range(10):
        task = f"test-task-{index}"
        source = root / "data/external" / task
        source.mkdir()
        row = copy.deepcopy(original_row)
        row["instance_id"] = task
        row_path = source / "row.json"
        row_path.write_text(json.dumps(row))
        media = source / "bug.gif"
        media.write_bytes(f"distinct-media-{index}".encode())
        report = copy.deepcopy(original_report)
        report.update(task=task, row_sha256=digest(row_path), raw_logs=str(source.relative_to(root)))
        for side in ["pre", "post"]:
            (source / (side + ".log")).write_bytes((root / "data/external/case" / (side + ".log")).read_bytes())
        proof = source / "proof.json"
        proof.write_text(json.dumps(report))
        annotation = copy.deepcopy(template)
        annotation["id"] = task
        annotation["source"].update(instance_id=task, row_path=str(row_path.relative_to(root)), row_sha256=digest(row_path))
        annotation["media"].update(path=str(media.relative_to(root)), sha256=digest(media))
        annotation["oracle"].update(report_path=str(proof.relative_to(root)), report_sha256=digest(proof))
        path = folder / (task + ".json")
        path.write_text(json.dumps(annotation))
        paths.append(path)
        pinned.append(row)
        reviews[task] = {"oracle_alignment": "direct", "media_sha256": digest(media),
                         **{key: annotation["claims"][0][key] for key in ("t_start_s", "t_end_s", "text")}}
    (root / "evals/reviews.json").write_text(json.dumps({"cases": reviews}))
    monkeypatch.setattr("svh.corpus.rows", lambda source: iter(pinned))
    return root, paths


def test_frozen_corpus_rejects_overwrite_and_changed_annotation(admitted_corpus):
    root, paths = admitted_corpus
    original = freeze_corpus(root, paths, Path("frozen.json"))
    manifest, annotations = load_frozen_corpus(root, Path("frozen.json"))
    assert len(annotations) == 10
    assert manifest["corpus_sha256"] == original["corpus_sha256"]
    with pytest.raises(FileExistsError):
        freeze_corpus(root, paths, Path("frozen.json"))
    paths[0].write_text(paths[0].read_text() + "\n")
    with pytest.raises(ValueError, match="Hash mismatch"):
        load_frozen_corpus(root, Path("frozen.json"))


def test_forged_pass_cannot_shrink_frozen_evaluation_denominator(admitted_corpus):
    root, paths = admitted_corpus
    manifest = freeze_corpus(root, paths, Path("frozen.json"))
    manifest["annotations"] = manifest["annotations"][:1]
    identity = {key: manifest[key] for key in ("dataset", "revision", "annotations")}
    manifest["corpus_sha256"] = hash_text(json.dumps(identity, sort_keys=True, separators=(",", ":")))
    manifest["gate"]["passed"] = True
    (root / "frozen.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="admission gate"):
        load_frozen_corpus(root, Path("frozen.json"))
