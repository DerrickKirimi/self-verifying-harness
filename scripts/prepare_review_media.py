"""Download only the selected public temporal assets for M0 annotation review.

No claims/reviews are generated here. Contact sheets must be inspected before
an annotation is admitted. Assets and sheets stay in the ignored source folder.
"""

import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from svh.corpus import probe


def main():
    root = Path("data/external/swebench-multimodal")
    paths = sorted((root / "cases").glob("*.json"))
    inventory = {}
    output = Path("notes/runs/m0-media-inventory.json")
    for row_path in paths:
        row = json.loads(row_path.read_text())
        task = row["instance_id"]
        urls = re.findall(r'https?://[^\s<>"\]\)]+\.(?:gif|mov|mp4|webm)', row["problem_statement"])
        if not urls:
            continue
        url = urls[0]
        if urlsplit(url).hostname != "user-images.githubusercontent.com":
            raise ValueError("Unreviewed download origin")
        case = root / "cases" / task
        case.mkdir(exist_ok=True)
        media = case / ("media" + Path(urlsplit(url).path).suffix)
        if task == "bpmn-io__bpmn-js-1655":
            media = root / "pilot.mov"
        if not media.exists():
            print(task, "downloading review asset", flush=True)
            with urlopen(Request(url, headers={"User-Agent": "svh-eval-curation"}), timeout=60) as response:
                data = response.read(40 * 1024 ** 2 + 1)
            if len(data) > 40 * 1024 ** 2:
                raise ValueError("Media exceeds the bounded download limit")
            media.write_bytes(data)
        info = {"source_url": url, "path": str(media), "sha256": hashlib.sha256(media.read_bytes()).hexdigest(),
                **probe(media), "review_interval_s": 0.5, "review_state": "unreviewed"}
        if info["duration_s"] > 180:
            raise ValueError("Long media needs an explicit review plan")
        if not list(case.glob("review-*.png")):
            subprocess.run([
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(media),
                "-vf", "fps=2,scale=320:-1,tile=6x4", "-fps_mode", "vfr", str(case / "review-%03d.png"),
            ], check=True, timeout=120)
        info["sheets"] = [str(path) for path in sorted(case.glob("review-*.png"))]
        inventory[task] = info
        output.write_text(json.dumps(inventory, indent=2) + "\n")
        print(task, round(info["duration_s"], 3), "seconds; sheets:", len(info["sheets"]), flush=True)


if __name__ == "__main__":
    main()
