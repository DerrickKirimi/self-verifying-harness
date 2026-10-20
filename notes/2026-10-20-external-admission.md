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

[CODE/INF] Oracle alignment is separately reviewed in `evals/reviews.json`.
Case 1578's fail/pass run is real, but the failing test checks copied subprocess
diagram-object identity. It does not reproduce the recorded pool-copy/export
failure or assert distinct process IDs. Its annotation was therefore moved out
of admission into `evals/excluded/`; proof snapshots are retained. This correction
prevents a native benchmark pass from silently verifying a broader claim. Two
additional directly aligned candidates, 1640 and 1928, have been reviewed and
queued for their own Docker runs. No oracle result is inferred from inspection.

```sh
uv sync --locked --extra datasets
uv run python -I scripts/run_m0_oracles.py
uv run python -I scripts/admit_reviewed_cases.py
uv run svh validate evals/annotations/swebench-bpmn-1655.json
uv run svh eval-gate --annotations evals/annotations --output notes/runs/m0-gate.json
```

[CODE] Curation resumes from hash-checked reports. Keep running Docker processes
alive; a quiet process is not evidence of a hang. The batch handles one task at
a time and preserves at least 15 GiB of free disk before further pulls.

## Reproduce from a new clone

[CODE] Raw media, rows and execution logs are deliberately absent from Git. A
fresh clone must download the pinned data and execute its own oracles. Historical
proof metadata alone does not make `svh validate` pass without matching raw logs.
The explicit rerun uses already recorded image digests where available; it does
not replace them with today's mutable image tags. This takes Docker storage and
CPU time, but no model credits. Do not run beside an already active batch.

```sh
uv sync --locked --extra datasets
uv run python -I scripts/prepare_m0_source.py
uv run python -I scripts/prepare_review_media.py
uv run python -I scripts/run_m0_oracles.py --rerun
uv run python -I scripts/admit_reviewed_cases.py --refresh-proofs
uv run svh eval-gate --annotations evals/annotations --output notes/runs/m0-gate.json
```

[CODE] Recorded manual reviews apply only to identical media hashes. New bytes
must be reviewed again; downloading a replacement never grants admission. A
refresh retains historical proof snapshots and validates fresh logs before
replacing annotation references. The current corpus is still being assembled;
the final command must fail until the required sample and interval are met.

[SRC/CODE] Shared Gemini access is authorized, with prepaid credit evidence and
auto-reload disabled. Private configuration uses the external secret file, never
key bytes in this repository. `svh.budget` implements atomic persistent worst-case
request reservations, retains ambiguous charges, and only releases a reservation
after metered settlement. Concurrent requests cannot oversubscribe the local cap;
restarts cannot silently increase it. Five budget tests pass; total suite is now
49 passed. No transport is connected yet. Before paid calls, bind reservations to
verified model prices/token limits, disable retries and optional paid tools.
Provider-side cap enforcement is delayed; it cannot replace that guard. No paid
model calls have been made for this checkpoint. A project-local ledger cannot
account for unrelated simultaneous consumption of the shared account.
