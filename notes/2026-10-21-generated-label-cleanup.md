# A second distinct generated repair: DI label cleanup

[RUN] Fresh method `probed-v2`, case1638 candidate1, generated a browser check
that confirms an existing DI label, calls the real `modeling.updateLabel` with
empty text, then requires the label property to be absent. Actual Chrome fails
at that final property assertion on buggy source. The recorded developer-console
symptom and stated requirement concern that property itself; downstream tool
impact is not separately verified. Alignment review is explicitly AI-assisted.

[RUN] Gemini3.5FlashLite/low then generated a source-only change in
`lib/features/label-editing/cmd/UpdateLabelHandler.js`, replacing `di.label = null`
with `delete di.label`. The identical frozen generated check passes after this
fix, and independent native regressions pass:1772 executed passes, seven unchanged
skips,1779 discovered. Supplied native test changes were added only after model
source generation. No supplied gold source fix entered the model context.

[RUN] The frozen public task is `tasks/generated-v2/swebench-bpmn-1638`.
Its proof pins the model-generated source/check bytes and actual pre/post/native
observations; raw traces remain ignored under `data/runtime/m3/probed-v2/`.
This task uses the generated check plus native regressions; the earlier1679
task's finite wrong-fix/identifier-variation controls are not claimed for this one.

[RUN] The six-considered-case snapshot remains **2/11 [5.14%,47.70%]** full
generated repairs, with five cases not attempted. The M3 gate does not pass.
Exact snapshots: `notes/runs/m3-probed-v2-after-1638-{report,score}.json`.
No v1 success is substituted into this v2 rate.

[RUN] Actual Harbor trials for the new task both pass: nop reward0 from the
completed target assertion failure; oracle reward1 from the unchanged generated
check and all native regressions passing. No trial exception was present.
`notes/runs/harbor-generated-v2-1638.json` pins the bundle and raw trial result/log
hashes. Job artifacts remain under `data/runtime/harbor-jobs/`. The package was
not edited after these trials. The launcher now explicitly disables Harbor
telemetry for future invocations, using the inspected pinned SDK's supported
`HARBOR_TELEMETRY=0`; this is not claimed to explain trial runtime.
