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
  narration no longer blocks the visual path. No external case has been verified.

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

## Next step

Next single unit: establish reuse permission and pilot CodeV's
`matplotlib__matplotlib-25631` video task in Docker against its base revision and
gold patch. Observe the supplied tests failing/passing ourselves; do not count
dataset metadata as verification. If unsuitable, pilot an E2E browser case.
See the public-dataset audit for exact source revisions and remaining checks.

Then bind annotations and recording hashes to oracle reports and assemble the
10–20-bug M0 set from accepted public cases and/or controlled recordings.
Owner clips in `docs/recording-guide.md` remain an option, especially for the
speech path, rather than a blocker. Do not begin M1 ingestion before M0 passes.
The harness-client question is still pending; it does not affect these fixtures.

## Gate results

| Milestone | Gate | Result | Date |
|---|---|---|---|
| M0 fixture checkpoint | Same pytest fails before / passes after | [RUN] 3/3; Wilson 95% [43.85%, 100%]; `notes/runs/fixture-oracle.json` | 2026-10-20 |
| M0 complete | 10–20 recorded annotated bugs; every reproduction fails before / passes after | Not passed: recordings/annotations and full sample missing | 2026-10-20 |
