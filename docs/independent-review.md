# Independent review of the grounded claims

[RUN/INF] The existing M2 rates use AI-assisted review. An independent human
review is still required by the prospective protocol. This packet prepares that
work; it does not claim that a human has performed it. No paid model calls are
needed. On the owner's current workspace the eleven source recordings and
contact sheets already exist. A fresh clone needs the vetted M0 corpus first;
see [external admission](../notes/2026-10-20-external-admission.md).

```sh
.venv/bin/python -I scripts/prepare_m2_review.py \
  --predictions notes/runs/m2-refined-media.json \
  --directory data/runtime/m2/refined-review-v3
cp -n evals/m2-human-review-template.json data/runtime/m2/independent-human-review.json
```

[CODE/RUN] The blank template binds the exact frozen predictions by SHA256 and
eleven independently hash-checked contact sheets. Its judgment fields are `null`,
so the scorer refuses it until decisions are explicit. It contains no copied
AI judgments or AI reasons. Use a new private filename for another reviewer;
do not overwrite the existing AI reviews or silently edit model predictions.

[INF] For each row, read the matching case in
`notes/runs/m2-refined-media.json`, open its `review_source.path`, and watch the
full recording listed in `evals/annotations/<recording_id>.json`. Check the
recording context before and after the predicted interval, rather than relying
only on selected frames or captions. The annotation's `claims` contains the
frozen reference behavior and interval; challenge an incorrect reference
explicitly instead of quietly changing it to fit the prediction. Do not consult
the previous AI judgment reasons before making your own decision.

For every prediction, replace the three null fields with booleans:

- `symptom_match`: does it describe the actual reported/observed bug?
- `expected_match`: does its proposed behavior match the reference requirement,
  without inventing a missing policy decision?
- `source_support`: does the cited recording support that symptom and interval?
  Expected behavior stated only in issue text must not be relabeled as visible.

[CODE/INF] Set `gold_claim_id` to the matching annotation claim ID for a semantic
match, write your own `reason`, and replace `scorer` with your human reviewer
identifier. Preserve the response, media and sheet hashes. An unresolved expected
behavior remains unresolved; do not supply the answer on the model's behalf.
Source hypotheses and a passing test are not substitutes for recording support.

```sh
.venv/bin/python -I scripts/score_m2.py \
  --predictions notes/runs/m2-refined-media.json \
  --judgments data/runtime/m2/independent-human-review.json \
  --checkpoints notes/runs/m2-checkpoints-media.json \
  --output data/runtime/m2/independent-human-score.json
```

[CODE/INF] Inspect the produced rates, sample sizes and Wilson intervals. A
numerical pass is evidence conditional on the recorded judgments; software
cannot authenticate that the reviewer is human. Keep the completed human review
and its provenance separate from the existing AI-assisted result. Record the
actual outcome in `STATUS.md`; a disagreement or failed gate must remain visible.
