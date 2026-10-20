# Remaining MVP completion requirements

[INF] M0/M1 and the M2 feature implementation are progress, not shipping proof.
This checklist preserves the original product scope before M3 is built.

- Normal task input must accept a registered recording, stated requirement,
  prepared Docker image and buggy commit **without requiring a supplied gold fix,
  supplied test or already-passing corpus admission**. The frozen M0 loader is an
  evaluation adapter, not the only product entry point. Keep private owner tasks
  and outputs ignored; public evaluation cases remain provenance-bound.
- Use the existing coding harness to generate a reproduction. Source must remain
  buggy during reproduction development. Freeze exact test bytes before trusting
  the observed pre-fix assertion failure. Setup/runtime crashes do not qualify.
- Only after that observation may the harness generate a source fix. Evaluate in
  a fresh sandbox containing only allowed source changes and the frozen check,
  not the agent's caches, altered test runners or fabricated output. Changed check
  bytes require a new candidate and a new pre-fix observation.
- Attempt all eleven frozen artifacts; include errors, ambiguity, abstention and
  budget exhaustion. Measure the fixed valid-reproduction confidence gate and
  separate repair rate, with at least one complete agent-generated recording ->
  check -> fix -> unchanged check pass -> held-out native regression demonstration.
- Include actual browser execution/observations for UI claims; do not substitute
  an unexecuted script or a model's description for a check. Keep code hypotheses,
  source-grounding scores and executable verification distinct.
- Challenge the end-to-end verifier with feature-deletion, error-suppression and
  visible-example shortcut controls where applicable. If an independent check is
  strengthened after a fix, observe its failure on the original buggy code too.
- Export every fully verified claim as a real Harbor task, including source/media
  references, immutable environment, generated frozen check and generated source
  solution. Execute real Harbor nop/oracle trials and record reward 0/1 on every
  exported task. A missing/timeout/setup reward is neither result.
- Provide usable setup/run/resume commands, source/response/proof hashes and
  final cost accounting. No real owner environment execution or credential
  exposure; no references' incidental database, agent-loop or cloud dependency.
- Audit actual artifacts and commands against the original idea, roadmap and
  prospective protocol before declaring the goal complete. Preserve narrow-data
  limits and the fact that M2 semantic judgments are AI-assisted, not independent
  human adjudication. No SaaS/live-call/multi-tenant features are required here.
