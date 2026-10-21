# Retained failures after financial-policy renewal

[RUN] The explicitly financially amended v5 continuation preserves the original
model, generation prompts, source context, runner and two-version case limit.
See `evals/m3-method-standard-submission-v5-renewed.json`; original evidence and
its expiry checkpoint remain unchanged.

[RUN] Case1570 candidate2 terminal: its executed viewport/rendered-position check
passes on base. The model subsequently tries to submit another distinct check,
which exceeds the case-wide two-version limit and is refused. Candidate1's final
reply had MAX_TOKENS with7860 output tokens all reported as reasoning; candidate2
ends with a ValueError after its second-version allowance is exhausted. No target
failure or source repair is trusted. Retained observations live under
`data/runtime/m3/standard-submission-v5/swebench-bpmn-1570/` (ignored).

[RUN] Case1623 candidate1 executes two distinct versions. The first ends in
`rootElement required`; the second ends in `Invalid Chai property: visible`.
Neither is a corrective target assertion. After the final stage error, the
controller mistakenly launches candidate2 before checking the actual version
count, then interrupts it during MCP startup before model generation. Its status
is explicitly `controller_cancelled_before_generation`, not a model outcome.
No third check runs. The ledger immediately before/after the cancellation remains
$7.518290 charged/reserved, with three prior unsettled reservations. Candidate2's
MCP log and report record remain retained. No source repair is authorized.

[INF] A useful release follow-up is an early controller preflight of exhausted
case versions before MCP/provider setup. The existing execution-time check
already refuses a third distinct version. Preserve these benchmark failures;
future interface improvements do not rewrite this run's outcomes.

[RUN] Case1659 candidate1 observes the actual stale label target assertion at
initial y415 after resizing an expanded SubProcess. Its model-generated
LayoutConnectionBehavior source change leaves that exact frozen assertion
failing; no valid fail/pass pair or native verification is claimed. Candidate2
then executes a different check containing literal escaped newlines in a module
array and fails JavaScript parsing. A subsequent distinct submission is refused
by the case-wide limit. Both candidates remain failures; no third version or
manual unescaping is permitted. At that checkpoint charged/reserved totals
$8.007896, leaving$4.187782 of the explicit new allowance. The original three
ambiguous reservations remain retained. Final case1719 is still pending.

[RUN] Case1719 candidate1 reaches actual collapse but fails because a missing
post-collapse label node yields null instead of literal false. The controller
rejects that failure: an absent node does not show the recorded wrongly visible
label. Candidate2 submits an empty check string, rejected by tool validation
before execution, then ends MAX_TOKENS with7863 output tokens all reported as
reasoning. No fix or extra candidate is authorized. The final all-eleven score
is in `notes/2026-10-21-m3-standard-submission-v5-results.md`; no stages remain
pending and all errors stay in the denominator.
