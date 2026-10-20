"""Create local source-frame contact sheets for human claim judgments."""
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, ImageDraw
from svh.evidence import Evidence

root = Path(__file__).resolve().parents[1]
evidence = Evidence.from_corpus(root, Path("evals/frozen-m0.json"))
report = json.loads((root / "data/runtime/m2/issue+media.json").read_text())
directory = root / "data/runtime/m2/review-frames"
directory.mkdir(parents=True, exist_ok=True)
reviews = []
for case in report["cases"]:
    if case["status"] != "completed":
        continue
    for prediction in case["predictions"]:
        if not prediction.get("span"):
            continue
        record = evidence.recording(case["id"])
        start = max(0, prediction["span"]["start_s"] - .5)
        end = min(record.duration_s, prediction["span"]["end_s"] + .5, start + 30)
        path = directory / (case["id"] + "-" + prediction["id"] + ".png")
        metadata_path = path.with_suffix(".json")
        if metadata_path.exists():
            prior = json.loads(metadata_path.read_text())
            if prior["response_sha256"] == case["response_sha256"]:
                reviews.append(prior)
                continue
            raise ValueError("Review sheet belongs to a different model response")
        frames = evidence.frames(record.id, start, end, 4)
        panels = []
        for timestamp, png in frames:
            image = Image.open(io.BytesIO(png)).convert("RGB")
            image = image.resize((800, round(image.height * 800 / image.width)))
            panel = Image.new("RGB", (800, image.height + 24), "white")
            panel.paste(image, (0, 24))
            ImageDraw.Draw(panel).text((8, 5), f"{record.id}: displayed source at {timestamp:.3f}s", fill="black")
            panels.append(panel)
        height = max(panel.height for panel in panels)
        sheet = Image.new("RGB", (1600, height * 2), "white")
        for index, panel in enumerate(panels):
            sheet.paste(panel, ((index % 2) * 800, (index // 2) * height))
        sheet.save(path)
        review = {"recording_id": record.id, "prediction_id": prediction["id"],
                  "response_sha256": case["response_sha256"], "media_sha256": record.sha256,
                  "timestamps_s": [timestamp for timestamp, _ in frames],
                  "path": str(path.relative_to(root)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        metadata_path.write_text(json.dumps(review, indent=2) + "\n")
        reviews.append(review)
(directory / "manifest.json").write_text(json.dumps(reviews, indent=2) + "\n")
print(json.dumps({"review_sheets": len(reviews), "directory": str(directory.relative_to(root))}))
