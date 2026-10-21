import hashlib
import json
from types import SimpleNamespace

import pytest
pytest.importorskip("langchain_core")
from svh import extract


def test_untrusted_claim_id_cannot_escape_its_artifact_directory():
    output = {"questions": [], "predictions": [{"id": "../../escape", "symptom": "reported bug",
               "expected_source": "issue", "observations": [], "span": None}]}
    with pytest.raises(ValueError, match="structure"):
        extract.validate_output(output, "issue-only", 3.0)


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
        _output_cap = 4096
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


def test_spoken_requirements_receive_transcript_and_bind_cached_response(tmp_path):
    transcript={'status':'transcribed','segments':[{'start_s':.2,'end_s':1.2,'speaker':'chunk_0:speaker_1',
                                                'text':'The label should stay yellow.'}]}
    class Evidence:
        corpus_sha256='owner-task'
        def recording(self, identifier):
            return SimpleNamespace(id=identifier,duration_s=2.0,sha256='media',has_audio=True)
        def transcript(self, *args):return transcript
        def frames(self, identifier, start, end, count):return [((start+end)/2,b'controlled-png')]
    calls=[]
    class Model:
        model='controlled';_output_cap=4096
        def invoke(self,messages):
            calls.append(messages)
            return SimpleNamespace(text=json.dumps({'predictions':[{'id':'spoken-claim','symptom':'Label turns white',
                'expected_behavior':'Label stays yellow','expected_source':'spoken',
                'span':{'start_s':.2,'end_s':1.2},'observations':[{'timestamp_s':.3,'detail':'Spoken: stay yellow'}]}],
                'questions':[]}),usage_metadata={},response_metadata={})
    task={'id':'owner','problem_statement':'Review this recording','issue_sha256':'issue'}
    path=tmp_path/'extraction.json'
    result=extract.extract_claims(Evidence(),task,'issue+media',Model(),path)
    assert result['predictions'][0]['expected_source']=='spoken'
    assert 'The label should stay yellow.' in str(calls[0][0].content)
    assert 'transcript_sha256' in result['identity']
    transcript['segments'][0]['text']='An updated transcript'
    with pytest.raises(ValueError,match='different inputs'):
        extract.extract_claims(Evidence(),task,'issue+media',Model(),path)
    with pytest.raises(ValueError,match='structure'):
        extract.validate_output({'predictions':result['predictions'],'questions':[]},'issue-only',2,allow_spoken=True)
