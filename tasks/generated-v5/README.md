# Generated SubProcess and empty-pool tasks

| Task | Actual native execution | Actual Harbor report |
|---|---|---|
|SubProcess property preservation1640|1776 passes,7 unchanged skips,1783 discovered|[nop0/oracle1](../../notes/runs/harbor-generated-v5-1640.json)|
|Empty-pool vertical space-tool resize1928|1889 passes,7 unchanged skips,1896 discovered|[nop0/oracle1](../../notes/runs/harbor-generated-v5-1928.json)|

[RUN] Both have generated source-only fixes and frozen checks observed failing
on base then passing unchanged. Their task directories are immutable after real
trials.1928 has no additional task-specific mutation sweep or ID variation.
Replay it without a model call, using a fresh run name:

```sh
.venv/bin/python -I scripts/run_harbor_integrity.py \
  --task tasks/generated-v5/swebench-bpmn-1928 --run-name my-1928-check
```

[RUN] `swebench-bpmn-1640` has a real generated source-only repair and unchanged
browser check observed failing before and passing afterward. Its independent
changed-ID/cardinality/condition check also has observed fail/pass. Native suite:
1776 executed passes, seven unchanged skips,1783 discovered. Finite deletion,
suppression and example-shortcut controls pass; this is not comprehensive
mutation coverage.

[RUN] Actual Harbor nop reward0 and oracle reward1 pass, including the primary,
independent variation and native regressions. Immutable bundle/proof identity:
[`harbor-generated-v5-1640.json`](../../notes/runs/harbor-generated-v5-1640.json).
Do not edit the task after those trials. The packaging-time `pending` field in
its manifest remains historical; the external trial report records the result.

```sh
.venv/bin/python -I scripts/run_harbor_integrity.py \
  --task tasks/generated-v5/swebench-bpmn-1640 --run-name my-1640-check
```

[CODE/INF] Use a fresh run name. Setup is in the root README. This replays frozen
generation outputs and needs no model call; it does not measure a student's
multimodal performance. The recording is referenced by source URL/hash rather
than redistributed. Existing distinct claims remain canonical under
`tasks/generated-v1/swebench-bpmn-1679` and
`tasks/generated-v2/swebench-bpmn-1638`; their immutable bundles remain unchanged.
