# M2 scoring fixed before generation

[CODE/INF] `evals/m2-rubric.json` fixes the eleven-case corpus, two conditions,
model, identical 4096-output-token cap and unchanged precision/recall Wilson
lower bounds >=0.50 over >=10 artifacts. No M2 generation has run yet.

[CODE] `svh.claims.score` requires every frozen artifact in the attempt list,
including errors/abstentions. Human judgments bind exact prediction-file bytes,
use explicit booleans and match each gold claim at most once. A semantic match
needs both symptom and expected behavior. A grounded match additionally needs
human-confirmed actual media support and a finite in-bounds source span.

[INF] The prospective span rule permits at most two seconds between generated
and gold intervals and at most five seconds of extra interval width. It prevents
an entire long recording from qualifying as a localized claim. Do not adjust
this rule after seeing outputs. Human reviewers must record the visual support
and mismatches without correcting model text. All model outputs remain intact.

[INF] Report semantic content metrics for both conditions and grounded metrics
separately. Issue-only outputs must not invent media timestamps and cannot
satisfy the grounded gate. Temporal-media input may use the public problem
statement to establish expected behavior, but that is not video-only inference.
The code checkpoint uses the existing deepagents loop in an isolated buggy
Docker checkout, with source locations and explicit hypotheses. A claim score
alone does not complete M2 without that working checkpoint. No fix precedes the
frozen failing reproduction in M3.

[RUN] Three tests cover judgment/input binding, denominator omission, duplicate
gold matches, truthy-string decisions, overbroad spans and semantic/grounded
separation. No paid request or generated code has run for M2.
