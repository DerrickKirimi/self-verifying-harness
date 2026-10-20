"""Local semantic retrieval over the exact same timestamped caption evidence."""

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

MODEL = "google/embeddinggemma-2"
REVISION = "914f7f89142e33e77833254d9c9b90c3cef7303b"


def file_sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def observation_query(query):
    """Focus a bug report on its observed effect rather than desired behavior.

    Claims in this project separate an observed symptom from an expected rule.
    Preserve the raw query in evaluation reports; add no source information.
    """
    observed = re.split(r"(?<=[.!?])\s+", query.strip(), maxsplit=1)[0]
    contrast = re.split(r"\b(?:but|while)\b", observed, flags=re.IGNORECASE)
    if len(contrast) > 1:
        effect = contrast[-1].strip()
        if re.search(r"\b(?:leaves?|remains?|unchanged|fails?|missing|wrong|behind|not)\b", effect, re.IGNORECASE):
            return effect
    return observed


class Embedder:
    def __init__(self, root: Path):
        import torch
        from sentence_transformers import SentenceTransformer
        torch.set_num_threads(4)
        self.path = root / "data/external/embeddinggemma-2" / REVISION
        # No network fallback, pickle weights, custom downloaded Python or GPU.
        self.model = SentenceTransformer(str(self.path), device="cpu", local_files_only=True,
            trust_remote_code=False, config_kwargs={"vision_config": None, "audio_config": None},
            model_kwargs={"dtype": torch.float32, "use_safetensors": True})
        self.model.max_seq_length = 512

    def documents(self, documents):
        return self.model.encode_document(documents, batch_size=8, normalize_embeddings=True,
                                          show_progress_bar=False, convert_to_numpy=True)

    def query(self, text):
        return self.model.encode_query([text], normalize_embeddings=True, show_progress_bar=False,
                                       convert_to_numpy=True)[0]


@lru_cache(maxsize=1)
def embedder(root: Path):
    return Embedder(root)


def build(root, caption_path, destination):
    import numpy as np
    index = json.loads(caption_path.read_text())
    identity = {"caption_sha256": file_sha(caption_path),
                "model": MODEL, "revision": REVISION, "mode": "text-only", "max_seq_length": 512,
                "caption_identity": index["identity"]}
    manifest_path = destination.with_suffix(".json")
    if manifest_path.exists():
        prior = json.loads(manifest_path.read_text())
        if prior["identity"] != identity or prior["vectors_sha256"] != file_sha(destination):
            raise ValueError("Semantic index has different inputs or vector bytes")
        return prior
    documents = [frame["caption"] + " " + frame["screen_text"] for frame in index["frames"]]
    vectors = embedder(root).documents(documents)
    if vectors.shape != (45, 768) or not np.isfinite(vectors).all():
        raise ValueError("Unexpected semantic vector shape or nonfinite values")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("xb") as stream:
        np.save(stream, vectors, allow_pickle=False)
    manifest = {"identity": identity, "vectors_sha256": file_sha(destination),
                "timestamps_s": [frame["timestamp_s"] for frame in index["frames"]]}
    with manifest_path.open("x") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    return manifest


def retrieve(root, recording_id, query, limit=5, *, focus_observation=False):
    import numpy as np
    if (not re.fullmatch(r"[A-Za-z0-9_-]{1,100}", recording_id)
            or not isinstance(query, str) or not 0 < len(query) <= 2000
            or type(limit) is not int or not 1 <= limit <= 5):
        raise ValueError("Request one to five results")
    # Called only after the evidence registry validates this opaque identifier.
    path = root / "data/runtime/semantic-index" / (recording_id + ".npy")
    manifest = json.loads(path.with_suffix(".json").read_text())
    caption_path = root / "data/runtime/visual-index" / (recording_id + ".json")
    identity = manifest["identity"]
    if (identity["model"] != MODEL or identity["revision"] != REVISION
            or identity["caption_sha256"] != file_sha(caption_path)):
        raise ValueError("Semantic index provenance mismatch")
    if manifest["vectors_sha256"] != file_sha(path):
        raise ValueError("Semantic vector bytes changed")
    vectors = np.load(path, allow_pickle=False)
    query_vector = embedder(root).query(observation_query(query) if focus_observation else query)
    scores = vectors @ query_vector
    if vectors.shape != (45, 768) or not np.isfinite(scores).all():
        raise ValueError("Invalid semantic index")
    positions = np.argsort(-scores, kind="stable")[:limit]
    return [{"timestamp_s": manifest["timestamps_s"][int(position)], "score": float(scores[position])}
            for position in positions]
