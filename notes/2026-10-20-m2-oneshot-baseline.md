# One-shot M2 baseline: gate failed

[RUN] All eleven cases completed in each matched condition, with one generated
claim per case. Model/prompt/corpus/rubric identities and raw response hashes are
frozen in `notes/runs/m2-oneshot-issue-only.json` and `m2-oneshot-media.json`.
The sequential extraction worker (exec38364) is terminal; do not restart it.

[RUN] Explicit judgments bind the exact files. **The scorer is Codex (AI), using
manual visual/source review, not independent human adjudication.** Eleven local
contact sheets were actually viewed, with the recorded sampled timestamps,
media hashes and image hashes retained in media judgments. Media itself remains
ignored/reference-only. Model text and time spans were not corrected.

| Condition, n=11 claims/artifacts | Content precision and recall | Grounded precision and recall |
|---|---|---|
| Issue-only | 10/11, Wilson95 [62.26%,98.38%] | 0/11 [0%,25.88%] |
| Issue + ordered media | 9/11, Wilson95 [52.30%,94.86%] | 7/11 [35.38%,84.83%] |

[RUN/INF] The grounded gate fails; a code checkpoint has not run. These are
subjective AI-assisted judgments on the curated development set, not population
accuracy estimates. Video did not uniformly improve semantic extraction: 1623
introduced an incorrect early-navigation trigger. Its cited frames still show
the overlay on return, while the missing-overlay event is later. 1659's almost
whole-clip interval fails the fixed width rule. 1928's cited resize-handle phase
does not clearly establish the space-tool-specific trigger. 1557 leaves two
alternative expected policies unresolved, without asking a clarification.

[RUN/INF] 1638 is accepted as an issue-grounded internal-property requirement
with independently visible label clearing and null-related linter failures.
Its internal object property is not visually proven. Likewise none of these
source-grounding judgments verifies software behavior: M3 still needs actual
frozen executable assertion failure, generated source repair and passing
independent regressions.

[INF] The next candidate is the planned codebase checkpoint with independent
media reinspection: treat first-pass claims and times as fallible, inspect early,
claimed and later states, narrow the actual failure interval, ask about ambiguous
requirements and preserve code causes as hypotheses. It may return refined claims
but must retain this failed baseline and leave the source unchanged. Run matched
checkpoint conditions with the same model/output/step caps. No gold claim, test,
patch or grader reaches that agent. Corpus and scoring thresholds stay fixed.

[RUN] Total settled API cost after extraction: **$0.643397** across 41 requests;
no unsettled reservations. **$3.356603** remains under the local cap. Proof:
`notes/runs/m2-oneshot-budget.json`. No model-generated code command has run yet.
