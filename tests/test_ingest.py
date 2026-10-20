import pytest
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
pytest.importorskip("langchain_core")

from svh.ingest import retrieve, parse_json, caption_recording, transcribe_recording
from svh.evidence import Evidence, Recording


def test_retrieval_localizes_and_never_interprets_query_as_sql():
    index = {"frames": [{"timestamp_s": 1, "caption": "menu open", "screen_text": "Copy"},
                         {"timestamp_s": 2, "caption": "orange label", "screen_text": ""},
                         {"timestamp_s": 3, "caption": "label becomes pale fill color", "screen_text": ""}]}
    assert retrieve(index, "pale fill color")[0]["timestamp_s"] == 3
    assert retrieve(index, "   ") == []
    assert retrieve(index, '"; DROP TABLE frames; --') == []
    assert retrieve(index, "Copy")[0]["timestamp_s"] == 1
    assert retrieve(index, "pale", "temporal3")[0]["timestamp_s"] in (2, 3)
    with pytest.raises(ValueError):
        retrieve(index, "color", limit=100)
    assert parse_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_caption_grid_stays_inside_media_and_resume_never_calls_model(tmp_path):
    duration = 6.816667
    record = SimpleNamespace(duration_s=duration, sha256="a" * 64)
    calls = []
    class FakeEvidence:
        corpus_sha256 = "b" * 64
        def recording(self, identifier):
            return record
        def frames(self, identifier, start, end, count):
            assert 0 <= start < end <= duration
            return [((start + end) / 2, b"controlled-png")]
    class FakeModel:
        model = "test"
        def invoke(self, messages):
            calls.append(messages)
            frames = [{"index": n, "caption": "red rectangle", "screen_text": ""} for n in range(45)]
            return SimpleNamespace(text=json.dumps({"frames": frames}), usage_metadata={}, response_metadata={})
    destination = tmp_path / "index.json"
    result = caption_recording(FakeEvidence(), "id", FakeModel(), destination)
    assert len(result["frames"]) == 45
    assert caption_recording(FakeEvidence(), "id", FakeModel(), destination) == result
    assert len(calls) == 1


def test_audio_decode_timestamp_validation_resume_and_evidence_access(tmp_path):
    media = tmp_path / "controlled.wav"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                    "sine=frequency=440:duration=2", str(media)], check=True, timeout=20)
    record = Recording("audio", media, hashlib.sha256(media.read_bytes()).hexdigest(), 2.0, True, "audio", "controlled")
    evidence = Evidence([record], "b" * 64)
    class FakeModel:
        model = "test"
        calls = 0
        def invoke(self, messages):
            self.calls += 1
            return SimpleNamespace(text=json.dumps({"segments": [{"start_s": .1, "end_s": 1.5,
                 "speaker": "speaker_1", "text": "controlled fixture"}]}), usage_metadata={})
    model = FakeModel()
    destination = tmp_path / "transcript.json"
    transcript = transcribe_recording(evidence, "audio", model, destination)
    assert transcribe_recording(evidence, "audio", model, destination) == transcript
    assert model.calls == 1
    served = Evidence([record], "b" * 64, transcripts={"audio": transcript})
    assert served.transcript("audio", 0, 1)["segments"][0]["speaker"] == "chunk_0:speaker_1"
    assert served.transcript("audio", 1.6, 2)["segments"] == []
    with pytest.raises(ValueError):
        served.transcript("audio", 0, 3)


def test_gif_sampling_preserves_final_hold_and_uses_preceding_frame(tmp_path):
    media = tmp_path / "held.gif"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                    "testsrc=size=32x32:rate=2:duration=1", "-final_delay", "500", str(media)],
                   check=True, timeout=20)
    record = Recording("held", media, hashlib.sha256(media.read_bytes()).hexdigest(), 5.5, False, "animated_image", "controlled")
    evidence = Evidence([record], "b" * 64)
    first = evidence.frames("held", .05, .15, 1)[0][1]
    second = evidence.frames("held", .6, .7, 1)[0][1]
    held = evidence.frames("held", 4, 4.1, 1)[0][1]
    assert first != second
    assert second == held
