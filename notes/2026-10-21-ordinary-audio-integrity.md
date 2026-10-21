# Ordinary audio run completes actual Harbor integrity

[RUN] `ordinary-audio-v3` completes the normal manifest route, with synthetic
narration plus an explicit fixture-author clarification. It does not read a
benchmark row, supplied source fix or supplied test patch. Extraction correctly
identifies the precise expected property as sourced from the written clarification
rather than pretending the garbled technical phrase was understood from speech.
The original unclarified inputs and both failed runs remain preserved.

[RUN] Actual generated browser assertion fails on buggy source, passes unchanged
after the generated source fix, and native regression coverage matches the
independently observed original baseline:1772 passes,seven unchanged skips,
1779 discovered on both. Source/check/report and baseline hashes are in
`notes/runs/ordinary-audio-v3-generated-repair.json`.

[RUN] Actual ordinary export completed under
`data/runtime/exports/ordinary-audio-v3/audio-clarified-e2e/`; no `native.diff`
exists in that package. Actual Harbor nop reward0 and oracle reward1 both pass,
with no trial exceptions. Report/bundle/result/log hashes:
`notes/runs/harbor-ordinary-audio-v3.json`. This development export stays ignored
and does not duplicate the canonical public1638 training task or change the
frozen public-corpus denominator.

[CODE] An unresolved extraction now returns its questions before launching
Docker/source inspection. A separate range bug was found in visual ingestion:
the fixed45 grid exceeded the evidence API's30s window above22.5 minutes. Sampling
now centers bounded windows on the same grid, including the one-hour limit.

[RUN] Ten targeted ingestion/preparation tests pass, including the one-hour
sampler range, early clarification output and retained failed checkpoint attempts.
Last full suite before these last two small changes:114 passed. No long-meeting
latency or speech-quality result is inferred from the synthetic fixture tests.

[INF] The implementation now has a measured ordinary recording-to-repair-to-task
path, but the all-case M3 acceptance gate and independent human claim adjudication
remain incomplete. Public1719 is being attempted next; do not call the full MVP
shipped based solely on this successful development run.
