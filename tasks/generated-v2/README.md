# Additional generated development tasks

[RUN] `swebench-bpmn-1638` clears a retained DI label property when its text is
removed. Its model-generated check was observed failing on buggy source and
passing unchanged after the model-generated fix, followed by1772 native passes
and seven unchanged skips. Actual Harbor nop reward0 and oracle reward1 both
pass: [integrity report](../../notes/runs/harbor-generated-v2-1638.json).

[CODE/RUN] The package includes the exact generated source/check, source license,
immutable environment and pre/post proof. Recording media is referenced by vetted
URL/hash, not redistributed. This package uses its generated check plus native
regressions; the earlier1679 task's additional wrong-fix controls are separate.

[INF] The earlier1679 task remains canonical under `tasks/generated-v1/` rather
than creating a duplicate instance for its v2 repeat. The all-eleven acceptance
gate remains incomplete. See [evidence](../../notes/2026-10-21-generated-label-cleanup.md)
and [running instructions](../../docs/mvp-usage.md).
