# Completed Standard submission run, with disclosed financial amendment

[RUN] The full eleven-case denominator is now considered, with zero pending
stages. The predeclared numerical M3 gate passes: **5/11** valid frozen
fail-before/pass-after pairs, Wilson95% **[21.27%,71.99%]**; **4/11** also pass
independent native regressions, Wilson95% **[15.17%,64.62%]**. Actual scorer:
`notes/runs/m3-standard-submission-v5-renewed-final-score.json`; exact retained
report: `notes/runs/m3-standard-submission-v5-renewed-final-report.json`.
No successes from v1/v2/v3/v4 are pooled into these counts.

[CODE/RUN] The original v5 model-access review expired mid-run. Its exact method,
report and score remain retained. Before resuming, the owner authorized $5 more
usage and a **financial-policy-only amendment** was explicitly frozen as
`evals/m3-method-standard-submission-v5-renewed.json`. The same model, tier,
thinking, generation/check/fix prompts, source packet, execution runner, corpus
and two-version limits remain unchanged. Authenticated limits and reviewed
prices are unchanged. The final result is an explicitly amended development
run with two financial-policy epochs, not a pristine single-implementation run
or a controlled ablation. Candidate records identify their method hashes.

| Case | Final evidence |
|---|---|
|1557|Abstains on unresolved contradictory policy; retained in denominator|
|1570|Two executed checks pass on base; no valid reproduction|
|1610|Exact generated check fails then passes, but native regression rejects the fix; not exported|
|1623|Two setup errors; mistaken second-stage launch cancelled before inference; no third check|
|1638|Candidate1 path rejected; candidate2 independently returns allowed path, exact fail/pass and1772 native passes|
|1640|Exact fail/pass and1776 native passes; additional independent variation and finite wrong-fix controls|
|1655|Reasoning-token exhaustion then rejected empty-style/stale-node evidence; no fix|
|1659|Actual stale-label failure; source fix leaves it failing; final version has a parse error|
|1679|Reasoning-token exhaustion then exact loop-type/XML fail/pass and1792 native passes; compiled-stack correction retained|
|1719|Rejected null-versus-false assertion on absent label; second candidate submits empty tool input, then exhausts reasoning tokens without a check|
|1928|Exact empty-pool resize fail/pass and1889 native passes|

[RUN] The four fully verified cases correspond to four distinct exported public
claims with actual Harbor nop0/oracle1: canonical1638 and1679 tasks already
contain source files byte-identical to the new repairs under the same base/image;
new1640 and1928 bundles have their own executed integrity reports. Do not create
duplicate claim exports. All native suites retain seven skips. References:
`notes/runs/harbor-generated-v2-1638.json`, `notes/runs/harbor-generated-v1-1679-buildx.json`,
`notes/runs/harbor-generated-v5-1640.json`, and
`notes/runs/harbor-generated-v5-1928.json`. Native-rejected1610 is never exported.

[RUN] Resumed paid usage increased the persistent charged/reserved estimate from
$7.195678 to **$8.454073**, a **$1.258395** increase. The new allowance retains
**$3.741605** under cumulative local cap$12.195678. All three uncertain requests
remain reserved; these are local conservative estimates, not a provider receipt.
No new paid call is needed for remaining release adapter checks.

[INF] **The full MVP is still not declared shipped.** Alignment and M2 numerical
judgments are AI-assisted; the independent human review required by the protocol
has not happened. `docs/independent-review.md` provides exact frozen review
packets and scoring commands. These are same-application development cases, not
held-out generalization, human speech quality or an arbitrary-repository result.
The no-paid-model README demo and ordinary synthetic-audio path are executable;
live phone/meeting integration and broader application adapters remain later work.
