import hashlib
import json
from types import SimpleNamespace

import pytest
pytest.importorskip("langchain_core")
from svh import extract


def test_dataset_row_allowlist_keeps_gold_out_of_model_tasks(tmp_path, monkeypatch):
    path = tmp_path / "row.json"
    path.write_text(json.dumps({"problem_statement": "Public issue", "patch": "PRIVATE_GOLD",
                                "test_patch": "PRIVATE_TEST", "FAIL_TO_PASS": ["PRIVATE_NAME"]}))
    annotations = [{"id": "case", "source": {"row_path": "row.json"},
                    "app": {"image": "immutable", "base_commit": "base"},
                    "claims": [{"text": "PRIVATE_ANNOTATION"}]}]
    monkeypatch.setattr(extract, "load_frozen_corpus", lambda root, path: ({"corpus_sha256": "frozen"}, annotations))
    identity, tasks = extract.public_tasks(tmp_path, "manifest")
    assert identity == "frozen"
    assert set(tasks[0]) == {"id", "problem_statement", "issue_sha256", "image", "base_commit"}
    assert "PRIVATE_" not in json.dumps(tasks)


@pytest.mark.parametrize("condition", ["issue-only", "issue+media"])
def test_matched_extraction_inputs_resume_and_timestamp_contract(tmp_path, condition):
    calls = []
    class Evidence:
        corpus_sha256 = "frozen"
        def recording(self, identifier):
            return SimpleNamespace(id=identifier, duration_s=2.0, sha256="media-sha")
        def frames(self, identifier, start, end, count):
            assert 0 <= start < end <= 2.0
            return [((start + end) / 2, b"controlled-image")]
    class Model:
        model = "controlled"
        def invoke(self, messages):
            calls.append(messages)
            prediction = {"id": "claim-1", "symptom": "a visible issue", "expected_behavior": "expected result",
                          "expected_source": "issue", "span": {"start_s": .5, "end_s": 1.5} if condition == "issue+media" else None,
                          "observations": [{"timestamp_s": 1.0, "detail": "shown"}] if condition == "issue+media" else []}
            return SimpleNamespace(text=json.dumps({"predictions": [prediction], "questions": [], "abstain_reason": None}),
                                   usage_metadata={}, response_metadata={})
    task = {"id": "case", "problem_statement": "Public issue", "issue_sha256": "issue-sha",
            "image": "not-model-visible", "base_commit": "not-model-visible"}
    destination = tmp_path / "raw.json"
    first = extract.extract_claims(Evidence(), task, condition, Model(), destination)
    assert extract.extract_claims(Evidence(), task, condition, Model(), destination) == first
    assert len(calls) == 1
    content = calls[0][0].content
    assert sum(item["type"] == "image_url" for item in content) == (45 if condition == "issue+media" else 0)
    assert "not-model-visible" not in str(content)
