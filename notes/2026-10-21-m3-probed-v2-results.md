# All-eleven browser-feedback evaluation

[RUN] `probed-v2` is terminal: all11 frozen cases considered,zero pending stages.
Both valid generated reproductions and full generated repairs are
**2/11,Wilson95% [5.14%,47.70%]**. The >=0.20 lower-bound gate fails.
Report/score snapshots: `notes/runs/m3-probed-v2-final-{report,score}.json`.
These are development-set results with explicitly AI-assisted alignment,
not independently human-adjudicated or unseen-application performance.

| Case | Outcome | Actual reason/evidence |
|---|---|---|
|1557|Abstained|Unresolved alternative requirements; no owner answer invented|
|1570|Setup failures|Both versions use invalid relocated helper/fixture imports|
|1610|Alignment rejected|Sets the current canvas root to itself; never switches planes|
|1623|Alignment rejected|Explicitly removes overlays, manufacturing the expected absence|
|1638|Verified repair|Frozen DI-label check fails/passes; native1772 passes/seven skips; exported Harbor0/1|
|1640|Setup failures|Invalid helper import, then synthetic event missing preventDefault|
|1655|Alignment rejected|Undefined wrong DI property; second version also expects the fill rather than stroke color|
|1659|No failing target|Invalid fixture import, then unrelated StartEvent move passes on buggy code|
|1679|Verified repair|Parallel loop-type check fails/passes and native regressions pass; stronger earlier canonical task already has Harbor0/1|
|1719|Setup failures|Invalid fixture import, then invalid label-parent object in generated setup|
|1928|Infrastructure then setup failures|Puppeteer cache lookup blocks first runs; exact frozen checks still fail on invalid helper imports after runner correction|

[RUN] Raw outputs, probe bytes, alignment reviews and source fixes remain under
`data/runtime/m3/probed-v2/`. No failed check was edited in place, no exhausted
case received a third distinct version, and no v1 or ordinary-input success was
pooled into this rate. The ordinary audio workflow's actual Harbor0/1 is a
separate development/functional result.

[RUN/CODE]1928 exposed trusted runner initialization occurring too late for newer
upstream Karma configuration. `PUPPETEER_EXECUTABLE_PATH` and `CHROME_BIN` are now
set before loading that configuration. Two exact frozen checks were reexecuted,
not replaced: Chrome starts but their helper imports fail. Evidence:
`notes/runs/m3-1928-runner-recovery.json`. An older image's exact known generated
check/fix still produces actual fail/pass under the corrected runner:
`notes/runs/browser-runner-chrome-init-compatibility.json`. Existing exported
bundles remain frozen, with their previously executed integrity proofs intact.

[INF] Next method should address the repeated relocated-import mistakes in
agent-visible base-spec examples and require the actual reported transition,
without manufacturing state or substituting a supporting invariant. Freeze a
new method before new calls; retain this failed run and unchanged rubric.

[RUN] Ledger at this checkpoint: $3.565270 estimated charged/reserved,$0.434730
available,zero unsettled,unchanged $4 cap. Do not raise/reset it. No model worker
remains active.
