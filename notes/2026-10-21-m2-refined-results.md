# M2 checkpoint/refinement measurement

[RUN] Both sequential checkpoint conditions finished all eleven frozen cases.
Every checkpoint inspected existing source and left its byte fingerprint unchanged.
Media checkpoints independently requested actual MCP frames. Exact outputs are
`notes/runs/m2-checkpoints-{media,issue-only}.json`; canonical model predictions
are frozen without correction in `m2-refined-{media,issue-only}.json`.

[RUN] Media grounded precision and recall are both **10/11**, Wilson 95%
**[62.26%,98.38%]**; the numerical gate and source-checkpoint gate pass in
`notes/runs/m2-refined-media-gate.json`. The earlier one-shot 7/11 failure remains
unchanged. Case 1557 explicitly asks which of two incompatible policies to use;
its expected behavior remains unresolved and is scored unsuccessful.

[RUN/INF] Scoring is Codex AI-assisted visual/source review, **not independent
human adjudication**. The prospective protocol requested a human scorer; that
validation remains outstanding. Numerical acceptance is sufficient to continue
engineering M3 autonomously, not to claim the requested human review occurred.
All eleven refined source sheets were inspected; exact prediction/media/frame
hashes and reasons are recorded in `m2-refined-media-judgments.json`.

[RUN] Issue-only refined content precision/recall are **9/11**, Wilson 95%
**[52.30%,94.86%]**. It has no video grounding (0/11). Besides ambiguity in 1557,
1679 focuses on isSequential updates rather than the observed serialized loop
*type*. Matched checkpoint model: Gemini 3.8 Flash, low thinking, 4096 output cap,
30 SDK graph steps. First-pass inputs use the same earlier Lite model. These are
curated development cases, not a causal study or unseen-app evaluation.

[RUN] Persistent budget at terminal batch: **$1.940127 settled**, **$2.059873
available**, zero unsettled requests, local cap **$4.00**. Failed pilots and
first-pass extractions remain charged and archived. Full suite last measured:
87 passed. No generated software reproduction or fix has yet been verified.
