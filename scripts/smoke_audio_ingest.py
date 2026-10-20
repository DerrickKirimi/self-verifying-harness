"""Functional timestamped-audio check using synthetic, non-private speech."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

from svh.evidence import Evidence, Recording
from svh.gemini import configured_model
from svh.ingest import transcribe_recording

root = Path(__file__).resolve().parents[1]
directory = root / "data/runtime/audio-fixture"
directory.mkdir(parents=True, exist_ok=True)
media = directory / "controlled.wav"
text = "The save button stays disabled after entering a valid project name."
if not media.exists():
    subprocess.run(["espeak-ng", "-s", "145", "-w", str(media), text], check=True, timeout=20)
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(media)],
                       check=True, capture_output=True, timeout=20)
duration = float(json.loads(probe.stdout)["format"]["duration"])
record = Recording("controlled-audio", media, hashlib.sha256(media.read_bytes()).hexdigest(), duration,
                   True, "audio", "synthetic espeak-ng speech; no human voice")
model = configured_model(root, output_cap=4096)
transcript = transcribe_recording(Evidence([record], "synthetic-functional-fixture"), record.id,
                                 model, directory / "transcript.json")
served = Evidence([record], "synthetic-functional-fixture", transcripts={record.id: transcript})
result = served.transcript(record.id, 0, duration)
words = lambda value: re.findall(r"[a-z]+", value.lower())
observed = " ".join(segment["text"] for segment in result["segments"])
report = {"passed": words(text) == words(observed) and bool(result["segments"]),
          "expected_text": text, "transcript": result, "duration_s": duration,
          "usage": transcript["usage"], "budget": model._budget.summary(),
          "scope": "One synthetic speech functional check; no speaker/meeting quality claim"}
(root / "notes/runs/audio-ingest-smoke.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(0 if report["passed"] else 1)
