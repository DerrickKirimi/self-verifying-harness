# MVP evaluation protocol

Set before the first model request. M0 has supplied-oracle observations; M1–M3
have no model measurements yet. Thresholds below are engineering acceptance
criteria, not published benchmark standards or population-quality guarantees.
Do not tune them after observing a result. [INF]

## Shared integrity rules

- Freeze the admitted corpus and record annotation hashes before a model run.
  Report excluded/pending cases separately. Curated admission is not a model
  success rate. Record model, harness/SDK versions, prompt hashes, token usage,
  spend, attempts, failures and timeouts. [INF]
- Agent-visible evidence excludes gold source patches, supplied test patches,
  grader scripts, test names and gold-derived notes. Generation uses a fresh
  buggy checkout without repository history exposing the solution. Evaluation
  runs separately with frozen tests. [INF]
- Report all admitted cases, including abstentions and exhausted budgets. Do
  not shrink a denominator to successful runs. Use Wilson 95% intervals for
  rates; report intervals as descriptive of this curated set, without claims of
  independent random sampling or cross-application generalization. [INF]
- Maintain separate measures for claim grounding, reproduction validity,
  held-out repair correctness and task-package integrity. A setup failure,
  inaccessible page or timeout is never an observed claim failure. [INF]

[CODE] `svh freeze-eval --output evals/frozen-m0.json` refuses an incomplete
admission gate or an existing destination. It records the exact annotation hashes
and a content identity. `svh.corpus.load_frozen_corpus` checks those bytes and
revalidates admission before a model evaluation; a saved pass flag cannot waive
the sample requirement. Freeze only after finishing the intended curation batch.

## M0: corpus admission

[CODE/INF] Existing gate: 10–20 distinct reviewed temporal artifacts; every
admitted supplied oracle fails by a target assertion before the source fix and
passes afterward with complete, unchanged regression coverage/skips. Wilson
lower bound >=0.70. Direct oracle-to-claim alignment and byte-bound provenance
are mandatory. Native oracle runs do not establish generated reproduction or
fix performance. See D21/D22/D24 and `svh eval-gate`.

## M1: ingestion, retrieval and MCP

[INF] Evaluate moment retrieval on every admitted claim with the same query
information across methods. Required comparison: fixed 45-frame caption baseline
and the selected temporal retrieval method. Use the roadmap's ±5 s criterion for
hit@1/hit@5; also report strict overlap, temporal distance and a midpoint-only
control because ±5 s is permissive on short clips. Do not present a saturated
short-clip metric as temporal understanding.

[INF] Minimum acceptance: selected retrieval hit@1 Wilson lower bound >=0.50
and hit@5 lower bound >=0.70, using at least ten distinct artifacts. Report the
baseline even if it wins; use the simpler method if a more complex one provides
no useful improvement. Embeddings, a vector database and scene selection remain
choices to test, not prerequisites imposed by the reference stack.

[INF] Demonstrate tools, resources, versioned prompts and structured/image
results through the selected MCP client over streamable HTTP. Record negotiated
protocol/capabilities and any fallback. Test origin/authorization boundaries,
trusted-argument injection, invalid handles and sandbox isolation. Every model
request must be covered by the persistent cost guard; no implicit retries.

[INF] Audio-bearing input needs a working timestamped transcript path; silent
media must return an explicit no-audio result. Diarization/transcription quality
requires a separate audio evaluation. Synthetic functional fixtures cannot
establish owner-meeting or third-party speaker accuracy. Preserve this scope in
the published result rather than inferring speech performance from GIFs.

## M2: grounded claims and codebase checkpoint

[INF] Evaluate precision and recall against the frozen human-reviewed claims on
at least ten artifacts. Match the observed symptom, expected behavior and source
span; a generic restatement without evidence is not a grounded match. Keep
uncertain expected behavior explicit and generate a clarification or abstention.
The checkpoint must inspect permitted code through the existing harness/MCP
tools, record supporting locations and distinguish evidence from hypotheses.

[INF] Minimum acceptance: both claim precision and recall Wilson lower bounds
>=0.50. Save model outputs and the matching judgments, including false positives
and abstentions. Run issue-text-only and temporal-media conditions with matched
model/budget where both inputs exist. The human scorer must not silently correct
generated text or count gold issue text as video-only inference.

## M3: self-verification and Harbor export

[INF] For every admitted case, attempt a reproduction before showing the agent
any fix. Freeze each candidate check, observe its target assertion fail on buggy
code, then let the existing coding harness attempt a source-only fix. Observe
that exact check pass afterward and run the held-out native regression suite.
A changed check starts a new candidate and needs a new pre-fix observation.
Retain all attempts and count budget exhaustion as unsuccessful.

[INF] Minimum acceptance: valid generated reproduction Wilson lower bound
>=0.20 over at least ten attempted distinct artifacts, and at least one complete
recording-to-generated-check-to-generated-fix demonstration with held-out
regressions passing. Report the separate full repair rate and its interval; a
generated check passing on a supplied gold patch is not an agent-generated fix.

[INF] Package every completely verified claim as a Harbor task with immutable
environment/source inputs, source-media references, instruction, frozen tests,
oracle solution and proof manifest. Run actual Harbor nop/oracle trials on every
exported task: nop must earn zero; oracle must earn one; setup/timeout/absent
reward cannot masquerade as either outcome. Verify package consistency with
the observed generated check and fix, rather than exporting the benchmark gold
patch as if it were the agent's work.

[INF] On the end-to-end demonstration, challenge the verifier with explicitly
authored wrong-fix controls: feature deletion, error suppression and a shortcut
for the visible example where applicable. Record expected and observed verdicts;
strengthen the independent checks if a control is falsely accepted. Do not call
a finite challenge set complete correctness or a comprehensive mutation score.

## Shipping evidence

[INF] MVP completion requires measured M0–M3 gates, reproducible setup/run
commands, a usable existing-harness/MCP integration, actual generated artifacts,
restricted Docker execution, recorded cost, complete proof bundles and executed
Harbor oracle/nop trials. Documentation, unit tests or supplied gold-oracle
curation alone cannot establish that the requested product is shipped.
