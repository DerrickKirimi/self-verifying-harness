# External temporal corpus admission

[CODE] The installed `svh.native` runner adapts the inspected BPMN/Karma contract
without importing the benchmark's agent loop. Source/test patches are separate;
the same frozen test patch runs before and after the source patch. Target failure
blocks must contain assertions; unrelated assertions, setup errors, incomplete
suites, reduced coverage and changed skips cannot verify a case.

[CODE] `svh.corpus` validates the pinned dataset bytes, exact row identity,
base commit and patch hashes, immutable image, source media URL, media SHA and
decoded duration/audio, timestamps, evaluation-script hashes and raw log hashes.
It recomputes native outcomes rather than trusting saved `verified` flags.
Admission proofs copy byte-identical logs into ignored content-addressed folders
and retain public metadata snapshots, independent of mutable curation reports.

[RUN] First external annotation validates; runner suite: 44 tests passed
(`.venv/bin/python -I -m pytest -q`). This establishes adapter integrity, not
claim extraction or generated reproduction performance.

[RUN] All twelve downloaded candidates were manually screened using every page
of 2 fps contact sheets; pilot 1655 additionally at 4 fps. No faces, credentials
or sensitive content were observed in those samples. Sampling does not establish
that every raw frame is clean. Review labels/times: `evals/reviews.json`; decoded
metadata and media hashes: `notes/runs/m0-media-inventory.json`. These are silent
visual artifacts; internal implementation details in claims also use issue text.

[INF] One application is deliberate initial scope. A curated pass rate cannot
estimate performance on arbitrary applications, recordings or narration. Gold
oracle curation is separate from subsequent blind generated-check evaluation.
Media stays reference-only: no redistribution or training rights are asserted.

```sh
uv sync --locked --extra datasets
uv run python -I scripts/run_m0_oracles.py
uv run svh validate evals/annotations/swebench-bpmn-1655.json
uv run svh eval-gate --annotations evals/annotations --output notes/runs/m0-gate.json
```

[CODE] Curation resumes from hash-checked reports. Keep running Docker processes
alive; a quiet process is not evidence of a hang. The batch handles one task at
a time and preserves at least 15 GiB of free disk before further pulls.

[SRC/INF] Shared Gemini access is authorized, with prepaid credit evidence and
auto-reload disabled. Private configuration uses the external secret file, never
key bytes in this repository. Before any metered call, implement and test local
worst-case request reservations, retain ambiguous charges, and disable retries.
Provider-side cap enforcement is delayed; it cannot replace that guard. No paid
model calls have been made for this checkpoint.
