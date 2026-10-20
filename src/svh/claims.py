"""M2 scoring; human judgments bind exact, unchanged model prediction bytes."""
import math

from svh.oracle import wilson


def score(predictions, judgments, annotations, rubric, prediction_sha256):
    if (judgments["prediction_sha256"] != prediction_sha256
            or predictions["corpus_sha256"] != rubric["corpus_sha256"]
            or judgments["condition"] != predictions["condition"]):
        raise ValueError("Judgments or predictions belong to different inputs")
    gold = {case["id"]: case for case in annotations}
    attempts = predictions["cases"]
    if len(attempts) != len(gold) or {case["id"] for case in attempts} != set(gold):
        raise ValueError("Every frozen artifact, including abstentions/errors, must remain in the denominator")
    decisions = {(row["recording_id"], row["prediction_id"]): row for row in judgments["predictions"]}
    if any(type(row.get(key)) is not bool for row in decisions.values()
           for key in ("symptom_match", "expected_match", "source_support")):
        raise ValueError("Judgment decisions must be explicit booleans")
    if len(decisions) != len(judgments["predictions"]):
        raise ValueError("Duplicate prediction judgment")
    generated, semantic, grounded, total_gold = 0, 0, 0, sum(len(case["claims"]) for case in annotations)
    seen_predictions = set()
    for attempt in attempts:
        gold_claims = {claim["id"]: claim for claim in gold[attempt["id"]]["claims"]}
        used_gold = set()
        for prediction in attempt["predictions"]:
            key = attempt["id"], prediction["id"]
            if key in seen_predictions or key not in decisions:
                raise ValueError("Duplicate or unjudged generated prediction")
            seen_predictions.add(key)
            generated += 1
            judgment = decisions[key]
            if not judgment["symptom_match"] or not judgment["expected_match"]:
                continue
            target = judgment["gold_claim_id"]
            if target not in gold_claims or target in used_gold:
                raise ValueError("Unknown or multiply matched gold claim")
            used_gold.add(target)
            semantic += 1
            span = prediction.get("span")
            if not judgment["source_support"] or not span:
                continue
            start, end = span["start_s"], span["end_s"]
            if (not all(isinstance(t, (float, int)) and math.isfinite(t) for t in (start, end))
                    or not 0 <= start < end <= gold[attempt["id"]]["media"]["duration_s"]):
                raise ValueError("Invalid generated source span")
            target = gold_claims[target]
            gap = max(target["t_start_s"] - end, start - target["t_end_s"], 0)
            extra_width = end - start - (target["t_end_s"] - target["t_start_s"])
            grounded += gap <= rubric["maximum_span_gap_s"] and extra_width <= rubric["maximum_extra_span_width_s"]
    if set(decisions) != seen_predictions:
        raise ValueError("Judgments contain predictions absent from the frozen output")
    def rate(numerator, denominator):
        return {"successes": numerator, "n": denominator, "wilson95": wilson(numerator, denominator)}
    result = {"artifacts": len(attempts), "content_precision": rate(semantic, generated),
              "content_recall": rate(semantic, total_gold), "grounded_precision": rate(grounded, generated),
              "grounded_recall": rate(grounded, total_gold)}
    result["claim_gate_passed"] = (predictions["condition"] == "issue+media"
        and len(attempts) >= rubric["minimum_artifacts"]
        and result["grounded_precision"]["wilson95"][0] >= rubric["precision_wilson_lower"]
        and result["grounded_recall"]["wilson95"][0] >= rubric["recall_wilson_lower"])
    return result
