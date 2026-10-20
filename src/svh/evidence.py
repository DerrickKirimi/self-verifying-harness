"""Read-only recording evidence. No generated code or model calls run here."""

from dataclasses import dataclass
import hashlib
import math
from pathlib import Path
import subprocess

from svh.corpus import load_frozen_corpus


@dataclass(frozen=True)
class Recording:
    id: str
    path: Path
    sha256: str
    duration_s: float
    has_audio: bool
    kind: str
    source_url: str

    def metadata(self):
        return {key: getattr(self, key) for key in
                ("id", "sha256", "duration_s", "has_audio", "kind", "source_url")}


class Evidence:
    def __init__(self, recordings, corpus_sha256):
        self.recordings = {record.id: record for record in recordings}
        if len(self.recordings) != len(recordings):
            raise ValueError("Duplicate recording identifier")
        self.corpus_sha256 = corpus_sha256

    @classmethod
    def from_corpus(cls, root, manifest):
        identity, annotations = load_frozen_corpus(root, manifest)
        recordings = []
        for item in annotations:
            media = item["media"]
            recordings.append(Recording(item["id"], (root / media["path"]).resolve(),
                                        media["sha256"], media["duration_s"], media["has_audio"],
                                        media["kind"], media["source_url"]))
        # Gold claims, test names, patches and grader paths never enter this store.
        return cls(recordings, identity["corpus_sha256"])

    def recording(self, recording_id):
        if recording_id not in self.recordings:
            raise ValueError("Unknown recording identifier")
        return self.recordings[recording_id]

    def frames(self, recording_id, t0, t1, max_frames=4):
        record = self.recording(recording_id)
        if (not all(math.isfinite(t) for t in (t0, t1))
                or not 0 <= t0 < t1 <= record.duration_s or t1 - t0 > 30):
            raise ValueError("Frame interval must be inside the recording and at most 30 seconds")
        if type(max_frames) is not int or not 1 <= max_frames <= 4:
            raise ValueError("Request between one and four frames")
        if hashlib.sha256(record.path.read_bytes()).hexdigest() != record.sha256:
            raise ValueError("Recording bytes changed after registration")
        output = []
        for index in range(max_frames):
            timestamp = t0 + (index + 0.5) * (t1 - t0) / max_frames
            result = subprocess.run([
                "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                "-protocol_whitelist", "file,pipe", "-ss", str(timestamp), "-i", str(record.path),
                "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2",
                "-f", "image2pipe", "-vcodec", "png", "-",
            ], capture_output=True, timeout=20)
            if (result.returncode or not result.stdout.startswith(b"\x89PNG\r\n\x1a\n")
                    or len(result.stdout) > 4 * 1024 ** 2):
                raise ValueError("Could not decode the requested frame within evidence limits")
            output.append((timestamp, result.stdout))
        return output

    def transcript(self, recording_id, t0, t1):
        record = self.recording(recording_id)
        if not all(math.isfinite(t) for t in (t0, t1)) or not 0 <= t0 < t1 <= record.duration_s:
            raise ValueError("Transcript interval must be inside the recording")
        if not record.has_audio:
            return {"recording_id": recording_id, "status": "no_audio", "segments": []}
        raise ValueError("This audio recording has not been transcribed")
