# SubProcess property repair and real Harbor integrity

[RUN] New distinct claim1640 completes under the prospectively frozen
`standard-submission-v5` method. A model-created real SubProcess has initial
parallel markers, cardinality and completion condition. The actual popup action
switches to sequential; its new marker/mode assertions pass, then cardinality
preservation fails. A model-generated source-only fix updates the existing
moddle object's mode through the modeling command API instead of replacing it.
The exact frozen check passes after that fix; no supplied gold source was shown
or exported. Coverage is this transition and the two configured properties,
not a universal all-state correctness guarantee.

[RUN] Held-out native regressions:1776 executed passes, seven unchanged skips,
1783 discovered. Proof:
`notes/runs/m3-standard-submission-v5-1640-generated-repair.json`.
Raw traces/observations remain in
`data/runtime/m3/standard-submission-v5/swebench-bpmn-1640/1/`.

[RUN] Six finite control runs in
`notes/runs/m3-standard-submission-v5-1640-controls.json` establish:

- An independent changed-ID/cardinality/condition check fails by target assertion
  on base and passes unchanged after the actual generated fix.
- Feature deletion and exception suppression are rejected by assertions.
- An authored recorded-ID shortcut passes the primary check but fails the
  independent variation. That variation is included in the task grader.

[RUN] Exported immutable task: `tasks/generated-v5/swebench-bpmn-1640`.
Actual sequential Harbor nop0/oracle1 trials pass primary, independent variation
and native integrity: `notes/runs/harbor-generated-v5-1640.json`.
No pending packaging marker was edited after the real trials.

[RUN/INF] This does not complete the all-case gate. The fresh v5 checkpoint is
1/11 [1.62%,37.74%], two considered/nine unattempted; earlier successes are not
pooled. Reviews remain AI-assisted, not independently human-adjudicated. The
owner's full MVP goal stays incomplete until its remaining gates/audit pass.

[RUN] Ledger after this generated repair: charged/reserved$5.234003, available
$6.765997 under the authorized cumulative$12 cap, three prior uncertain
reservations retained. Controls and Harbor trials make no model calls.
