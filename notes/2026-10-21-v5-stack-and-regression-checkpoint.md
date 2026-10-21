# Compiled stack correction and a rejected regression

[RUN] Fresh v5 now has **4/11 valid generated fail/pass pairs**, Wilson95%
**[15.17%,64.62%]**, and **3/11 full native-passing repairs**,
**[9.75%,56.56%]**. Six cases considered/five unattempted at this snapshot;
the gate does not pass. Report/score:
`notes/runs/m3-standard-submission-v5-after-1679-{report,score}.json`.
These are AI-assisted development judgments, not independent human scoring.

[RUN] The controller initially rejected1679 by mapping browser stack line numbers
onto the original JavaScript. That interpretation was wrong: webpack transforms
the module. Trusted CDP capture of the actual loaded module shows lines75/106
are the MultiInstanceLoopCharacteristics assertions, after the popup assertions
pass. The exact frozen check/source archive match the original observation.
The previous review remains preserved; the corrected review and actual loaded
source identities are in
`notes/runs/m3-standard-submission-v5-1679-stack-review.json`.
No generated check was edited or extra candidate granted.

[RUN] The first three source-capture attempts failed before capture; their
ignored raw logs remain under the candidate. The working diagnostic uses an
explicit container-local debugging port and retains the completed Karma iframe
long enough to capture loaded source. It changes no app source or generated
check, makes no model call, and is not itself used as a fail/pass oracle.
For another ambiguous generated-check stack:

```sh
.venv/bin/python -I scripts/inspect_compiled_check.py \
  --candidate-directory data/runtime/m3/RUN/CASE/CANDIDATE \
  --name stack-inspection-1
```

[CODE/INF] Use a new diagnostic name. It prints the actual loaded source at the
reported stack lines. Check assertion semantics and setup context before
approving a repair; do not assume a constant compiled/original line offset.

[RUN]1679 then completes unchanged two-mode type/XML checks and1792 executed
native passes/seven unchanged skips (1799 discovered). Its source file is
byte-identical to the existing canonical generated task, whose real Harbor0/1
proof remains linked; no duplicate task is exported.

[RUN]1610 separately reproduces actual editor persistence after plane/breadcrumb
navigation. Its model repair passes that check, but the independent native suite
rejects loss of an unsaved edit. It is a valid reproduction pair, **not a full
verified fix**, and is not exported. Held-out regression details are not passed
to subsequent generation models. Both outcomes and source identities:
`notes/runs/m3-standard-submission-v5-1610-1679-outcomes.json`.

[RUN/INF]1655 remains rejected: nodes captured before the color action are not
requeried afterward, and observed computed style is empty rather than the
recorded wrong fill color. A stale-node artifact is possible and current-node
sampling is not established; no unsupported color oracle is trusted.

[RUN] Snapshot budget: charged/reserved$6.718164, available$5.281836 under the
authorized cumulative$12 cap; three uncertain reservations remain retained.
Subsequent1928 work is separate from this snapshot. Prior runs are not pooled.
