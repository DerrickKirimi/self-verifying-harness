"""Fetch the two pinned public Parquet files; never execute downloaded code.

Rows are exported only after both SHA256 values match the inspected release.
Run with uv run python -I scripts/prepare_m0_source.py.
"""

import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

from svh.sources import DATASET, FILES, REVISION, export_rows


def main():
    source = Path("data/external/swebench-multimodal")
    destination = source / "data"
    destination.mkdir(parents=True, exist_ok=True)
    for filename, expected in FILES.items():
        target = destination / filename
        if target.exists():
            if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
                raise ValueError("Existing source bytes differ from the pinned release: " + filename)
            print(filename, "already hash-verified")
            continue
        url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/data/{filename}"
        partial = target.with_suffix(".partial")
        checksum = hashlib.sha256()
        total = 0
        try:
            with urlopen(Request(url, headers={"User-Agent": "svh-pinned-eval"}), timeout=90) as response, partial.open("wb") as output:
                while chunk := response.read(1024 * 1024):
                    total += len(chunk)
                    if total > 100 * 1024 * 1024:
                        raise ValueError("Source exceeds the bounded download limit")
                    checksum.update(chunk)
                    output.write(chunk)
            if checksum.hexdigest() != expected:
                raise ValueError("Downloaded source differs from the pinned release")
            partial.replace(target)
        finally:
            partial.unlink(missing_ok=True)
        print(filename, "downloaded and hash-verified")
    # Selection is explicit and fixed, not filtered by a model's success.
    import json
    reviews = json.loads(Path("evals/reviews.json").read_text())
    selected = export_rows(source, list(reviews["cases"]))
    print("Exported", len(selected), "reviewed candidate rows")


if __name__ == "__main__":
    main()
