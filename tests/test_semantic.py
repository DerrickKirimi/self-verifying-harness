"""Local vector integrity/ranking, with no download or real model inference."""
import json
import pytest

np = pytest.importorskip("numpy")
from svh import semantic


def test_observation_query_keeps_failure_separate_from_desired_behavior():
    assert semantic.observation_query("Changing a setting clears its value. The value should persist.") == "Changing a setting clears its value."
    assert semantic.observation_query("The arrow moves while its label remains behind. Both should move.") == "its label remains behind."
    assert semantic.observation_query("The menu opens while the page loads.") == "The menu opens while the page loads."


@pytest.mark.parametrize('ordinary',[False,True])
def test_semantic_index_binds_caption_bytes_and_preserves_timestamps(tmp_path, monkeypatch,ordinary):
    calls = []
    class ControlledEmbedder:
        def documents(self, documents):
            calls.append(documents)
            return np.eye(45, 768, dtype=np.float32)
        def query(self, query):
            vector = np.zeros(768, dtype=np.float32)
            vector[42] = 1
            return vector
    monkeypatch.setattr(semantic, "embedder", lambda root: ControlledEmbedder())
    storage=tmp_path/'data/runtime/task-evidence'/'manifest-hash' if ordinary else tmp_path/'data/runtime'
    captions = storage / "visual-index/controlled.json"
    captions.parent.mkdir(parents=True)
    index = {"identity": {"recording_id": "controlled", "media_sha256": "a" * 64,
                           "corpus_sha256": "b" * 64},
             "frames": [{"timestamp_s": float(n), "caption": str(n), "screen_text": ""} for n in range(45)]}
    captions.write_text(json.dumps(index))
    destination = storage / "semantic-index/controlled.npy"
    manifest = semantic.build(tmp_path, captions, destination)
    assert semantic.build(tmp_path, captions, destination) == manifest
    assert len(calls) == 1
    options={'index_root':storage} if ordinary else {}
    results = semantic.retrieve(tmp_path, "controlled", "controlled question",**options)
    assert results[0]["timestamp_s"] == 42.0 and results[0]["score"] == 1.0
    assert len(results) == 5
    with pytest.raises(ValueError):
        semantic.retrieve(tmp_path, "../../.env", "question",**options)
    destination.write_bytes(destination.read_bytes() + b"tamper")
    with pytest.raises(ValueError, match="bytes changed"):
        semantic.retrieve(tmp_path, "controlled", "question",**options)
