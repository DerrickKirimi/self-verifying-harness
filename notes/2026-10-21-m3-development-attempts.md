# M3 generation development attempts

[RUN] `data/runtime/m3/generated-v1/report.json` retains all eleven corpus rows.
The first two cases with completed candidate budgets (1655 and 1638) have **no
valid recording-derived reproduction**. No generated source fix has been attempted.
Actual Chrome runs and raw SDK traces remain ignored beside each frozen check.

- 1655 candidate1: a DI color assertion fails, but a second test raises a setup
  error and the DOM helper import is invalid. Rejected, not partially counted.
  Candidate2 exhausts SDK graph steps before a final check (ExceptionGroup).
- 1638 candidate1: initial setup assertion fails before the intended action;
  directEditing API usage and an unresolved DOM helper are not reliable. Explicit
  alignment review rejects this despite an assertion-shaped failure.
  Candidate2: wrong initial fixture text and a retained SVG node cause unrelated
  assertion failures. Explicit alignment review rejects it too.
- 1570 candidate1: passes on buggy code. Default viewport and no completed-wrap
  invariant do not expose the reported transition. Rejected. Candidate2 is active
  in exec61955; inspect that exact handle rather than duplicating its paid work.

[CODE/INF] These are development attempts with evolving generation implementation;
not a clean model benchmark. The original 30-step SDK cap and maximum two
candidates per case remain. After repeated searches exhausted a stage, generation
uses read-only tool exposure with an eight-call limit, actual MCP media first,
and the SDK's typed final-output tool retained. No custom model/agent loop.
Later prompt guidance requires actual absolute source paths, inspected fixture
identifiers, content-mode grep, standard DOM APIs and re-querying rendered nodes.
Each raw trace records prompt/model/policy; early pilot traces predate policy tags.

[CODE/RUN] Ordinary task input now runs extraction and code checkpoint without
benchmark admission/gold. Documentation: `docs/mvp-usage.md`. Native regressions
for such input use the existing base suite; the public eval adapter additionally
stages held-out benchmark tests outside model access. Neither ordinary-task full
repair nor Harbor task integrity has yet been measured.

[CODE/RUN] Harbor 0.24.0, local clean commit
4b94505a91c5ddcb70b5740ac95718ddee13e5a0, installed into a separate ignored venv.
The exporter guards observed fail/pass, alignment review, generated-source hashes
and independent regressions; uses schema 1.4 and a separate source-only verifier.
Its integrity unit test passes. This is **not** an executed nop/oracle trial.

[RUN] Before the active 1570 second candidate: $2.338882 settled, $1.661118
available, zero unsettled requests. Cap unchanged at $4.00. Last full suite:
93 passed; an additional denominator integrity test also passes in a targeted run.

[RUN] Later checkpoint: 1570 candidate2 also passes on buggy source and is
rejected. 1640 candidate1 returns an empty typed check; candidate2 fails typed
output validation after inspection. Neither reaches a trusted claim assertion.
No extra candidates are added to exhausted cases.

[RUN/INF] Two tiny integration diagnostics return nonempty typed fields both with
and without prior tool history (`notes/runs/m3-typed-output{-history,}-probe.json`).
Therefore a universal final-tool transport failure is **not established**. The
empty case output remains a generation/context failure pending diagnosis; do
not attribute it categorically to the SDK. Both diagnostics together settle
$0.000947. Total after diagnostics: $2.678613, remaining $1.321387, no pending.

[CODE/RUN] Existing-source packet retrieval now supplies buggy source, related
base specs/fixtures and bottom-of-spec helpers, without supplied patches or grader
context. First actual packet metadata: `notes/runs/m3-base-source-packet-smoke.json`.
The tool-exposure cap is ten for subsequent attempts (still within the original
30 graph steps). This evolving development run is not a fixed-method benchmark.
Ordinary task registration + actual authenticated MCP PNG retrieval passes:
`notes/runs/normal-task-mcp-smoke.json`; replay `scripts/smoke_normal_task.py`.
Full suite: 94 passed. Case1679 candidate1 now runs sequentially in exec19601.
