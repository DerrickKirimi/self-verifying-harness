# Flash Flex capacity and submission checkpoint

[RUN] `content-flash-flex-v4` remains **incomplete**: three of eleven cases
considered, eight unattempted, no active worker and no verified generated pair.
Snapshots: `notes/runs/m3-content-flash-flex-v4-checkpoint-{report,score,errors-probes}.json`.
Do not combine these outputs with an earlier or later run to manufacture a pass.

[RUN]1557 retains its unresolved-policy abstention.1640 uses both executed check
versions on a passing fixture smoke and assertion-free DOM inspection; neither
reproduces the bug, and no third version is granted.1638 candidate1 generates a
real target assertion, but the final submission call returns HTTP503. Candidate2
completes an exact fresh-base reproduction for empty-string and null label input,
with initial/rendered assertions passing before the DI-label removal assertions
fail. Its frozen check is aligned, but the repair's final call also returns503.
No successful repair or post-fix pass is fabricated from those partial results.

[RUN] At this checkpoint: estimated settled$3.974304 across504 requests, uncertain
reservations$0.984679 across3 requests, total charged/reserved$4.958983, available
$7.041017 under the owner-authorized cumulative$12 cap. No uncertain reservation
is released. There is no automatically retried request or tier fallback.

[SRC] The official [Flex guide](https://ai.google.dev/gemini-api/docs/generate-content/flex-inference),
read2026-10-21, describes best-effort, sheddable capacity and503 when capacity is
unavailable. [RUN] The AI Studio status URL returned only an application shell;
it did not establish a general outage. [INF] Test Standard in a separately frozen
run rather than continuing this capacity-sensitive chain or claiming a diagnosed
global outage.

[CODE/INF] A second observed problem is that the internal tool's generic probe
framing permits wasting the two-version allowance on diagnostics. The next
method calls it `submit_browser_reproduction`, explicitly requires the reported
action/corrective assertions on the first submission, and repeats that contract
when read inspection is exhausted. This does not grant extra executed versions
or turn a passing smoke into a reproduction. Its effectiveness remains unmeasured.
