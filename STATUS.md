# Status

Update this file at the end of every working session: what changed, gate results with their numbers, and the next concrete step.

## Current milestone: M0 (eval set), in progress

- [CODE] A standalone Python/uv CLI now verifies three planted issue-board bugs:
  case-sensitive search, incorrect closed filtering and priority ordering.
- [RUN] All three reproductions fail by assertion on `426a532` and pass on
  `eee15eb`, using the same frozen tests in restricted Docker containers.
  Fixture rate: **3/3, 95% Wilson CI [43.85%, 100%]**. This is a curated fixture
  result, not a generalization estimate or completed M0 gate.
  Full logs, image ID, commits and hashes: `notes/runs/fixture-oracle.json`.
- [CODE] No ingestion, model calls, agent-generated fixes or Harbor packaging yet.
  No owner recordings are present. **M0 has not passed; the full MVP is not shipped.**
- [SRC] Owner clarified that reference projects must not become inherited constraints.
  D11–D16 in `docs/decisions.md` record this; retrieval/SDK choices remain open.
- [SRC] Docker is the current backend; E2B/Daytona or other backends can be added
  later (D17). Public video/task pairs are now candidates for M0 (D18), so owner
  narration no longer blocks the visual path.
- [RUN/SRC] SWE-bench Multimodal is now the selected primary visual-task source.
  Its official site reports a September 2026 v2 refresh. The pinned Parquet audit
  covers 580 rows and identifies 2 direct video-link tasks, 67 GIF-link tasks
  and 8 untyped-asset candidates (overlapping categories, not verified media).
  See `notes/2026-10-20-swebench-multimodal-pilot.md`.
- [RUN] **First external supplied-oracle pilot succeeded:** BPMN label color,
  1/1 case, Wilson 95% [20.65%, 100%]. Expected assertion fails before the gold
  fix; afterward all 1777 executed tests pass, with the same 7 skips in both
  runs. Proof: `notes/runs/swebench-bpmn-pilot.json`. Media annotation/admission
  and agent-generated reproductions remain unmeasured; M0 is not complete.
- [CODE/RUN] External annotation admission now binds the pinned Parquet row,
  base/patch/image hashes, decoded media and regraded raw logs. The first
  annotation (`evals/annotations/swebench-bpmn-1655.json`) validates. Runner
  integrity tests: **44 passed**. Twelve visual artifacts have been manually
  screened at 2 fps (the pilot additionally at 4 fps); reviews and timestamped
  claims are in `evals/reviews.json`. Raw media stays ignored/reference-only.
- [RUN] A sequential 12-candidate Docker curation batch is running. Durable
  progress: `notes/runs/m0-curation-progress.json`; command:
  `.venv/bin/python -I scripts/run_m0_oracles.py`. Existing reports are regraded
  on resume. Do not infer completion from the progress file alone; inspect
  reports/raw logs. The second candidate's pre-run has a target runtime error
  rather than an assertion and currently cannot satisfy strict admission.
- [CODE/RUN] A persistent SQLite cost ledger now reserves request upper bounds
  atomically, retains ambiguous charges across restarts and refuses silent cap
  increases. Concurrent-reservation and settlement checks pass; total runner
  suite: **49 passed**. No model transport is wired to it yet and no metered
  calls have been made. Private local configuration is capped below the supplied
  prepaid balance; no key or billing screenshot is committed.
- [RUN] Current external admission gate: **4/4 admitted annotations, Wilson 95%
  [51.01%, 100%]**, below the required sample size and lower bound. This is
  `notes/runs/m0-gate.json`, not model performance. Cases 1557, 1570 and 1655
  and 1578 pass; 1567 was rejected because its target failure is a runtime
  exception. Candidate 1610 is running; remaining candidates are queued.
- [CODE/RUN] Fresh-clone source preparation now downloads and hash-verifies both
  pinned Parquet files, then exports the reviewed rows. An isolated temporary-root
  replay fetched both files and exported 12 rows successfully:
  `notes/runs/m0-source-replay-smoke.json`. Explicit `--rerun` and
  `--refresh-proofs` support fresh local oracle evidence without deleting public
  historical proof metadata. Full fresh-clone Docker replay remains unmeasured.
- [SRC] Owner explicitly requested a side agent for a relevance-ranked literature
  review. `/root/literature_review` is researching primary sources and writing
  `docs/literature-review.md` plus reference entries; main work continues on M0.

## Log

- **2026-10-17. Bootstrap.**
  - Added the idea files verbatim to `docs/idea/` (byte-identical to `~/swe/llms/devagent/next-projects/`, checked with sha256).
  - Wrote `docs/analysis.md`, `docs/roadmap.md`, `docs/decisions.md`, `docs/references.md`, `AGENTS.md`, `CLAUDE.md`, and the M0 annotation schema in `evals/schema/`.
  - No code yet.

- **2026-10-20. First executable M0 checkpoint.**
  - [RUN] Built a Docker pytest image using an immutable Python base and pinned
    Python dependencies; Docker daemon version observed: 29.7.2.
  - [RUN] Observed the three assertions fail before applying app fixes;
    raw initial evidence is in `notes/runs/pre-fix.json`. The classifier was
    corrected for pytest's alternate `AssertionError: assert ...` format before
    collecting that saved pre-fix run. No test was changed to obtain a pass.
  - [CODE] Added `svh verify`, `svh serve --revision pre|post`, `svh validate`,
    the fixture manifest, recording guide, and integrity/annotation tests.
  - [RUN] Final checks: 22 tests passed; both recording-server revisions served
    expected HTML and shut down cleanly. See `notes/2026-10-20-m0-checkpoint.md`
    and `notes/runs/recording-server-smoke.json`.
  - [CODE] The current CLI is intentionally scoped to hand-written fixtures;
    annotation validation checks structure/files/times, not decoded media or
    the truth of spoken content. Fixture reports do not fill `observed` fields.
  - [SRC] Checked the current MCP specification and Claude Code HTTP MCP docs;
    Claude Code is a provisional first client, not a required runtime dependency.
  - [RUN/SRC] Audited public candidates: E2E Tests Dataset has 10 MP4s across
    five documented regression cases at the inspected revision; CodeV's video-only
    subset has one task with fix/test patches. Full findings, pinned revisions,
    current limitations and source URLs: `notes/2026-10-20-public-dataset-audit.md`.
  - [RUN] Selected SWE-bench Multimodal as the primary visual source and completed
    the first native external Docker oracle. Pinned Parquet audit and BPMN pilot:
    `notes/2026-10-20-swebench-multimodal-pilot.md`. Final runner checks: 27 tests
    passed. All raw media/gold patches stay under ignored `data/external/`.

## Next step

The live curation command currently has exec session **97904**. Poll that handle
while available; do not start a duplicate batch. If that process has actually
ended, inspect progress and resume the same command. No API calls are pending.

Finish the sequential native-oracle batch, freeze proofs for passing candidates,
and admit reviewed annotations with
`.venv/bin/python -I scripts/admit_reviewed_cases.py`, then `svh eval-gate`.
The provenance adapter and
first admission are implemented. Curation includes one application only; do not
present it as cross-application or speech evaluation. Admission requires 10–20
distinct artifacts, every oracle passing, Wilson lower bound >=0.70 (D22).

Then assemble the 10–20-bug M0 set from reviewed video/GIF candidates in the pinned
SWE-bench Multimodal release, supplementing from other sources when necessary.
Use the two direct-video tasks as anchors; inspect untyped assets before
asserting video coverage. Do not present GIF-only cases as narrated recordings.
Owner clips in `docs/recording-guide.md` remain an option, especially for the
speech path, rather than a blocker. Do not begin M1 ingestion before M0 passes.
Coding-harness client integration remains M1 work; the current gate is independent
of that client and does not require another owner decision.

## Gate results

| Milestone | Gate | Result | Date |
|---|---|---|---|
| M0 fixture checkpoint | Same pytest fails before / passes after | [RUN] 3/3; Wilson 95% [43.85%, 100%]; `notes/runs/fixture-oracle.json` | 2026-10-20 |
| External native oracle pilot | Supplied test fails before / passes after gold patch | [RUN] 1/1; Wilson 95% [20.65%, 100%]; `notes/runs/swebench-bpmn-pilot.json` | 2026-10-20 |
| M0 complete | 10–20 recorded annotated bugs; every reproduction fails before / passes after | Not passed: recordings/annotations and full sample missing | 2026-10-20 |
