# Status

Update this file at the end of every working session: what changed, gate results with their numbers, and the next concrete step.

## Current milestone: M0 (eval set), in progress

- [CODE] First local issue-board fixture and three pytest HTTP reproductions prepared.
  The initial app revision deliberately contains search, closed-filter and priority-sort bugs.
- [RUN] All three reproductions observed failing by assertion on `426a532`, before any
  app fix was applied. Raw pytest/JUnit output: `notes/runs/pre-fix.json`.
- No post-fix results or owner recordings yet; M0 has not passed.

## Log

- **2026-10-17. Bootstrap.**
  - Added the idea files verbatim to `docs/idea/` (byte-identical to `~/swe/llms/devagent/next-projects/`, checked with sha256).
  - Wrote `docs/analysis.md`, `docs/roadmap.md`, `docs/decisions.md`, `docs/references.md`, `AGENTS.md`, `CLAUDE.md`, and the M0 annotation schema in `evals/schema/`.
  - No code yet.

## Next step

Answer open question 1 in `docs/decisions.md` (which app for M0). Then record the first 3 walkthroughs, with annotations that validate against `evals/schema/walkthrough.schema.json`, and run each reproduction on its pre-fix and post-fix commits. Log the results here.

## Gate results

| Milestone | Gate | Result | Date |
|---|---|---|---|
| M0 | Every reproduction fails before the fix and passes after | — | — |
