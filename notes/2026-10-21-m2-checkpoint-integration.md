# Existing-harness checkpoint and independent reinspection

[CODE] The checkpoint uses deepagents' graph, official MCP evidence tools and
Docker backend. There is no new model/tool decision loop. We consume graph
states only to retain episode evidence across errors. The evidence-server child
receives no model credentials; provider retries and schema-repair retries are
disabled. All model calls, including middleware, use the shared reservation guard.

[CODE] The agent inspects lib source and, in the media condition, early/claimed/
later frames. A completed checkpoint must include actual MCP metadata, source
inspection and at least two frame calls/three distinct samples for media. Exact
workspace-byte fingerprints must remain unchanged. Source locations must exist,
with valid line numbers; file hashes and surrounding context are recorded.
Locations and hypotheses do not verify a bug or fix. Only the later executable
oracle can do that.

[RUN] Earlier pilots are retained in
`notes/runs/m2-checkpoint-failed-pilots.json` and ignored raw episodes. Both v1
conditions hit the graph limit. Bounded-v2 produced malformed issue-only JSON
and again exhausted the media graph. No ambiguous charges remain. Root-default
file searches now map to /workspace, and fixed Python helpers use isolated mode;
actual SDK read/glob smoke checks pass in the public image.

[CODE/RUN] The next candidate uses Gemini 3.8 Flash, low thinking, 4096 output
tokens, 30 graph steps in both conditions and an SDK structured terminal tool
with handle_errors=False. Primary documentation read 2026-10-20 UTC confirms low
thinking support (minimal is unsupported). Policies are preserved in
`evals/m2-checkpoint-v3.json` and `m2-checkpoint-v4.json`; scoring thresholds and
initial frozen claims are unchanged. The media v3 pilot completes with source
unchanged and actual frame reinspection. The issue-only v3 pilot incorrectly
supplied a zero-width placeholder span and was rejected, without correction.
The v4 issue-only tool structurally omits all media fields; absent fields map to
null/empty in the common scorer representation, while provided extra timestamps
are rejected. Its pilot completes with source unchanged.

[RUN] Final matched batch is running sequentially in exec93013: media v3 first,
then issue-only v4, reusing each successful pilot. Do not restart while live.
All eleven cases stay in each report. It is not yet a measured M2 pass. Scoring
remains AI-assisted manual review, explicitly not independent human adjudication.
The full suite passes **87 tests**, including claim-ID path bounds and the
issue-only schema rejecting rather than correcting invented timestamps.

[CODE] Commands:

```sh
.venv/bin/python -I scripts/run_m2_checkpoints.py --condition 'issue+media' --run-name flash-typed-v3 --model gemini-3.8-flash --max-steps 30
.venv/bin/python -I scripts/run_m2_checkpoints.py --condition issue-only --run-name flash-control-v4 --model gemini-3.8-flash --max-steps 30
.venv/bin/python -I scripts/collect_m2_refined.py --checkpoints data/runtime/m2/checkpoints-flash-typed-v3/issue+media.json --output notes/runs/m2-refined-media.json
```

[INF] Once terminal, freeze outputs, inspect their source frames, bind new
judgments to those bytes and run score_m2 with the corresponding checkpoint
report. Preserve the failed one-shot results. M3 remains gated on M2 completion.
