"""Read-only recording evidence. No generated code or model calls run here."""

from dataclasses import dataclass
from bisect import bisect_right
import hashlib
import math
import json
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
    def __init__(self, recordings, corpus_sha256, *, visual_indexes=None, transcripts=None, retrieval_method="fixed45", semantic_root=None, semantic_index_root=None):
        self.recordings = {record.id: record for record in recordings}
        if len(self.recordings) != len(recordings):
            raise ValueError("Duplicate recording identifier")
        self.corpus_sha256 = corpus_sha256
        self.visual_indexes = visual_indexes or {}
        self.transcripts = transcripts or {}
        self.retrieval_method = retrieval_method
        self.semantic_root = semantic_root
        self.semantic_index_root = semantic_index_root
        if retrieval_method not in {"fixed45", "temporal3", "embeddinggemma2", "embeddinggemma2-observation", "transcript_fts5"}:
            raise ValueError("Unknown server retrieval policy")
        if retrieval_method.startswith("embeddinggemma2") and semantic_root is None:
            raise ValueError("Semantic retrieval requires server-owned index paths")
        self._frame_times = {}
        for identifier, index in self.visual_indexes.items():
            record = self.recording(identifier)
            identity = index["identity"]
            if (identity["media_sha256"] != record.sha256 or identity["corpus_sha256"] != corpus_sha256
                    or identity["recording_id"] != identifier or len(index["frames"]) != 45):
                raise ValueError("Visual index does not match registered evidence")
            for frame in index["frames"]:
                if (not math.isfinite(frame["timestamp_s"]) or not 0 <= frame["timestamp_s"] <= record.duration_s
                        or any(not isinstance(frame[key], str) for key in ("caption", "screen_text"))):
                    raise ValueError("Invalid visual index")
        for identifier, transcript in self.transcripts.items():
            if transcript["media_sha256"] != self.recording(identifier).sha256:
                raise ValueError("Transcript does not match registered evidence")

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
        indexes, transcripts = {}, {}
        for record in recordings:
            for kind, target in (("visual-index", indexes), ("transcripts", transcripts)):
                path = root / "data/runtime" / kind / (record.id + ".json")
                if path.exists():
                    target[record.id] = json.loads(path.read_text())
        policy_path = root / "data/runtime/retrieval-policy.json"
        policy = json.loads(policy_path.read_text()) if policy_path.exists() else {}
        if policy and policy["corpus_sha256"] != identity["corpus_sha256"]:
            raise ValueError("Retrieval policy belongs to a different corpus")
        return cls(recordings, identity["corpus_sha256"], visual_indexes=indexes, transcripts=transcripts,
                   retrieval_method=policy.get("method", "fixed45"), semantic_root=root)

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
        if record.kind == 'audio':
            return []
        if hashlib.sha256(record.path.read_bytes()).hexdigest() != record.sha256:
            raise ValueError("Recording bytes changed after registration")
        if record.sha256 not in self._frame_times:
            probe = subprocess.run(["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe",
                "-select_streams", "v:0", "-show_entries", "frame=best_effort_timestamp_time",
                "-of", "json", str(record.path)], capture_output=True, timeout=30)
            if probe.returncode:
                raise ValueError("Could not read source frame timestamps")
            times = [float(frame["best_effort_timestamp_time"]) for frame in json.loads(probe.stdout)["frames"]]
            if not times or any(not math.isfinite(time) for time in times) or times != sorted(times):
                raise ValueError("Invalid source frame timeline")
            self._frame_times[record.sha256] = times
        output = []
        for index in range(max_frames):
            timestamp = t0 + (index + 0.5) * (t1 - t0) / max_frames
            # Display the most recent frame, including a GIF's final held image.
            # Seeking chooses the next packet and can silently shift the evidence.
            frame_index = max(0, bisect_right(self._frame_times[record.sha256], timestamp) - 1)
            result = subprocess.run([
                "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error",
                "-protocol_whitelist", "file,pipe", "-i", str(record.path),
                "-frames:v", "1", "-vf", f"select='eq(n,{frame_index})',scale='min(1280,iw)':-2",
                "-fps_mode", "vfr",
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
        if hashlib.sha256(record.path.read_bytes()).hexdigest() != record.sha256:
            raise ValueError('Recording bytes changed after registration')
        if not record.has_audio:
            return {"recording_id": recording_id, "status": "no_audio", "segments": []}
        if recording_id in self.transcripts:
            transcript = self.transcripts[recording_id]
            return {"recording_id": recording_id, "status": transcript["status"],
                    "speaker_scope": transcript["speaker_scope"],
                    "segments": [segment for segment in transcript["segments"]
                                 if segment["end_s"] >= t0 and segment["start_s"] <= t1]}
        raise ValueError("This audio recording has not been transcribed")

    def find_moment(self, recording_id, query, limit=5):
        record=self.recording(recording_id)
        if not isinstance(query, str) or not 0 < len(query) <= 2000:
            raise ValueError("Supply a question of at most 2000 characters")
        if record.kind == 'audio':
            from svh.ingest import retrieve
            transcript=self.transcript(recording_id,0,record.duration_s)
            index={'frames':[{'timestamp_s':(s['start_s']+s['end_s'])/2,
                              'caption':s['text'],'screen_text':''} for s in transcript['segments']]}
            matches=retrieve(index,query,'fixed45',limit)
            return {'recording_id':recording_id,'method':'transcript_fts5',
                    'matches':[{'timestamp_s':m['timestamp_s'],'score':m['score'],'text':m['caption']} for m in matches],
                    'evidence_mode':'fallible timestamped transcript; reported behavior, not visible proof'}
        if recording_id not in self.visual_indexes:
            raise ValueError("Recording has not been visually indexed")
        if self.retrieval_method.startswith("embeddinggemma2"):
            from svh.semantic import retrieve
            matches = retrieve(self.semantic_root, recording_id, query, limit,
                               focus_observation=self.retrieval_method.endswith("-observation"),
                               **({'index_root':self.semantic_index_root} if self.semantic_index_root is not None else {}))
            for match in matches:
                frame = min(self.visual_indexes[recording_id]["frames"], key=lambda frame: abs(frame["timestamp_s"] - match["timestamp_s"]))
                match["caption"] = frame["caption"]
        else:
            from svh.ingest import retrieve
            matches = retrieve(self.visual_indexes[recording_id], query, self.retrieval_method, limit)
        return {"recording_id": recording_id, "method": self.retrieval_method,
                "matches": matches,
                "evidence_mode": "model_captions; view frames to confirm"}

    def screen_text(self, recording_id, t0, t1):
        record = self.recording(recording_id)
        if not all(math.isfinite(time) for time in (t0, t1)) or not 0 <= t0 < t1 <= record.duration_s:
            raise ValueError("Screen text interval must be inside recording")
        if record.kind == 'audio':
            return {'recording_id':recording_id,'status':'no_video','frames':[]}
        if recording_id not in self.visual_indexes:
            raise ValueError("Recording has not been visually indexed")
        frames = self.visual_indexes[recording_id]["frames"]
        return {"recording_id": recording_id, "evidence_mode": "model_read_screen_text; may contain errors",
                "frames": [{"timestamp_s": frame["timestamp_s"], "text": frame["screen_text"]}
                           for frame in frames if t0 <= frame["timestamp_s"] <= t1][:12]}
