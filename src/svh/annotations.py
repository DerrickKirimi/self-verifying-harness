"""Validate recorded evidence without executing reproduction files."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from svh.oracle import contained


def validate_annotation(root: Path, annotation: Path):
    data = json.loads(annotation.read_text())
    schema = json.loads((root / "evals/schema/walkthrough.schema.json").read_text())
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
    recording = contained(root / "evals/recordings", data["recording"]["path"])
    if not recording.is_file() or recording.stat().st_size == 0:
        raise ValueError(f"recording is missing or empty: {recording}")
    for claim in data["claims"]:
        if not 0 <= claim["t_start_s"] < claim["t_end_s"] <= data["recording"]["duration_s"]:
            raise ValueError("claim timestamps must be ordered and within recording duration")
        test = contained(root / "evals/reproductions", claim["reproduction"]["path"])
        if not test.is_file():
            raise ValueError(f"reproduction is missing: {test}")
    return data
