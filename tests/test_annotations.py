import json
from pathlib import Path

import pytest

from svh.annotations import validate_annotation


@pytest.fixture
def annotation(tmp_path):
    root = Path(__file__).resolve().parents[1]
    schema = tmp_path / "evals/schema/walkthrough.schema.json"
    schema.parent.mkdir(parents=True)
    schema.write_bytes((root / "evals/schema/walkthrough.schema.json").read_bytes())
    recording = tmp_path / "evals/recordings/demo.webm"
    recording.parent.mkdir()
    recording.write_bytes(b"test-placeholder-not-a-real-recording")
    test = tmp_path / "evals/reproductions/test_demo.py"
    test.parent.mkdir()
    test.touch()
    data = {"id": "demo", "app": {"repo": ".", "pre_fix_commit": "a", "post_fix_commit": "b"},
            "recording": {"path": "demo.webm", "duration_s": 10},
            "claims": [{"t_start_s": 1, "t_end_s": 2, "text": "demo", "kind": "bug",
                        "reproduction": {"path": "test_demo.py", "runner": "pytest"}}]}
    return tmp_path, data


@pytest.mark.parametrize("change,message", [
    (lambda d: d["claims"][0].update(t_start_s=3), "timestamps"),
    (lambda d: d["claims"][0].update(t_end_s=11), "timestamps"),
    (lambda d: d["recording"].update(path="missing.webm"), "missing or empty"),
    (lambda d: d["recording"].update(path="../../outside"), "escapes"),
    (lambda d: d["claims"][0]["reproduction"].update(path="missing.py"), "missing"),
])
def test_reject_invalid_evidence(annotation, change, message):
    root, data = annotation
    change(data)
    path = root / "annotation.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match=message):
        validate_annotation(root, path)


def test_valid_annotation_structure(annotation):
    root, data = annotation
    path = root / "annotation.json"
    path.write_text(json.dumps(data))
    assert validate_annotation(root, path) == data
