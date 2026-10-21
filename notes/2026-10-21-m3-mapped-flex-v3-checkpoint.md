# Mapped-reference Flex evaluation checkpoint

[CODE/INF] The method was frozen before evaluation calls in
`evals/m3-method-mapped-flex-v3.json`: the same eleven cases and rubric, public
buggy-source examples with explicitly mapped root imports, actual MCP frames,
Lite/Flex/medium and at most two distinct executed check versions per case.
Implementation and prompt hashes are pinned. No earlier success is pooled.

[RUN] Three cases have been considered, with eight unattempted. Case1557 retains
the explicit unresolved-policy abstention. No generated fail/pass pair has
completed in this run. This is not a passed gate. Current machine-readable
report/score/proofs are `notes/runs/m3-mapped-flex-v3-checkpoint-*.json`.

| Case/version | Actual outcome | Alignment decision |
|---|---|---|
|1640/1|Completed Chrome assertion failure after changing multi-instance mode|Rejected: exercises Task instead of the reported SubProcess and omits initial configured-value assertions|
|1640/2|Initial parallel mode/cardinality/condition assertions pass, actual popup switch reaches sequential mode, then cardinality assertion fails|Accepted for this direction and these two properties; repair returns an empty edit list and fails source validation, so no verified repair|
|1570/1|Completed Chrome failure on deep equality of entire viewbox object after creating a pool|Rejected: adding a pool legitimately changes content bounds; the assertion does not isolate viewport position/scale|

[RUN] The public-data provenance objection on the first1570 launch was resolved
by inspecting `extract.public_tasks`, `source_packet`, `generation`, the isolated
Docker backend and `evals/annotations/swebench-bpmn-1570.json`. Payloads are the
vetted public issue/GIF and public upstream BPMN-js source/specs, not private
harness source or host files. A subsequent review accepted the call and it ran.

[RUN] The next launch,1570 candidate2, **was not executed**: automatic approval
review failed because its service usage limit was reached. The message says to
retry at4:40PM; its timezone is not established here. This is a review-service
failure, not an unsafe-action determination or Gemini exhaustion. Do not bypass
approval review. No live model worker remains at this checkpoint.

[RUN] Subsequent owner correction: review capacity has refilled. The same1570
candidate2 command below was accepted and launched as exec29006. The stopped
report/score snapshots above remain historical evidence, not the live report.

[RUN] Last ledger read: estimated charged/reserved **$3.661200**, available
**$0.338800**, zero unsettled, unchanged **$4 cap**. Do not raise/reset it.
Next evaluation action, after approval review becomes available, is:

```sh
.venv/bin/python -I scripts/run_m3.py \
  --only swebench-bpmn-1570 --run-name mapped-flex-v3 \
  --stage reproduce --candidate 2 --model gemini-3.5-flash-lite \
  --service-tier flex --thinking medium
```

[INF] Preserve the earlier1640 repair failure. This command does not grant a
third distinct test version. Reinspect current budget, method hashes and model
policy freshness before proceeding, and do not start another worker if a current
one is confirmed live. Existing README demo and ordinary-input instructions are
unchanged; the fresh all-case acceptance gate and independent human M2 review
remain incomplete.

[RUN] Full harness suite after the new integration: **123 passed**, one expected
SDK warning from rejecting invalid tier `auto`. Commit `aab90ac` was pushed.
GitHub still reports pytest alert2 open, while the actual
`sandbox/requirements.txt` pins9.1.1 and the alert's patched threshold is9.0.3.
No dependency downgrade or alert dismissal was performed.
