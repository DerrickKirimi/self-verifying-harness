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

## Next step

Owner: record and annotate the first three walkthroughs using
`docs/recording-guide.md` (or identify a preferred existing app). Only the owner
can supply the required voice. Keep recordings local and out of commits.

Next implementation unit: connect validated annotations and recording hashes to
oracle reports, then expand the app/eval set to the required 10–20 bugs and
measure the complete M0 gate. Do not begin M1 ingestion before that gate passes.
The harness-client question is still pending; it does not affect these fixtures.

## Gate results

| Milestone | Gate | Result | Date |
|---|---|---|---|
| M0 fixture checkpoint | Same pytest fails before / passes after | [RUN] 3/3; Wilson 95% [43.85%, 100%]; `notes/runs/fixture-oracle.json` | 2026-10-20 |
| M0 complete | 10–20 recorded annotated bugs; every reproduction fails before / passes after | Not passed: recordings/annotations and full sample missing | 2026-10-20 |
