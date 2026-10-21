# Budget-limited mapped-reference evaluation

[RUN] `mapped-flex-v3` is terminal: all eleven cases considered, no active worker.
The method/rubric were frozen before its calls. No earlier success is pooled.
Final report, score and error/probe evidence:
`notes/runs/m3-mapped-flex-v3-final-{report,score,errors-probes}.json`.

| Cases | Actual outcome |
|---|---|
|1557|Explicit abstention on unresolved alternative requirements|
|1570|Whole-viewbox equality fails but is rejected for conflating content bounds and viewport position; second version's x/y assertions pass on buggy code; a further probe is refused by the case-wide two-version limit|
|1610|Provider ServerError before an answer; no retry, full uncertain reservation retained|
|1640|First version rejected for Task/SubProcess mismatch; second version observes the actual configured SubProcess transition lose cardinality; repair returns an empty edit list and fails validation|
|1623,1638,1655,1659,1679,1719,1928|Actual local BudgetExceeded before provider dispatch; no new paid call|

[RUN] Under the unchanged fail-before/pass-after rubric, valid generated pairs
and full repairs are both **0/11, Wilson95% [0%,25.88%]**. The gate fails.
Seven cases never reached the provider because of budget exhaustion, and one
failed on a provider error. This is a budget-limited development evaluation,
**not an isolated comparison of generation methods or model quality**. Alignment
judgments are AI-assisted, not independent human adjudication. The accepted1640
pre-fix assertion alone does not count as verification without unchanged post-fix
success. No new task qualifies for export.

[RUN] Ledger: **$3.693868** estimated settled usage across467 requests, plus one
uncertain **$0.167527** reservation. Total charged/reserved **$3.861395** against
the unchanged **$4** cap; available **$0.138605**. This is local accounting, not
a provider billing receipt or proof that the prepaid account is empty. The
remaining amount is below the selected model's full-context request reservation.
No reservation was released, cap raised, ledger reset, billing setting changed
or purchase made. Do not infer the precise HTTP code from the recorded ServerError
type; the retained error artifact does not establish it.

[RUN/CODE] Previously verified public1679/1638 bundles and the ordinary clarified
audio bundle retain their real Harbor nop0/oracle1 evidence. README replay works
without paid generation. The fresh all-case gate and independent human M2 review
remain incomplete, so the full MVP is not declared shipped.

[INF] Next: inspect actual provider balance/usage before buying more credit.
Additional spend requires explicit owner authorization and recorded funding
without erasing previous usage. Recheck dated model access/prices before another
run. Preserve this outcome; do not silently restart failed cases in the same
method or pool prior successes. Any method change needs a new prospective run.
