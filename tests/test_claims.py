import pytest

from svh.claims import score


def inputs():
    annotations = [{"id": str(n), "media": {"duration_s": 30},
                    "claims": [{"id": "gold", "t_start_s": 10, "t_end_s": 12}]} for n in range(11)]
    predictions = {"corpus_sha256": "frozen", "condition": "issue+media", "cases": [
        {"id": str(n), "predictions": [{"id": "pred", "span": {"start_s": 11, "end_s": 12}}]} for n in range(11)]}
    judgments = {"condition": "issue+media", "prediction_sha256": "exact-bytes", "predictions": [
        {"recording_id": str(n), "prediction_id": "pred", "gold_claim_id": "gold",
         "symptom_match": True, "expected_match": True, "source_support": True} for n in range(11)]}
    rubric = {"corpus_sha256": "frozen", "minimum_artifacts": 10, "precision_wilson_lower": .5,
              "recall_wilson_lower": .5, "maximum_span_gap_s": 2, "maximum_extra_span_width_s": 5}
    return predictions, judgments, annotations, rubric


def test_claim_gate_keeps_missing_attempts_and_binds_judgments():
    p, j, a, r = inputs()
    assert score(p, j, a, r, "exact-bytes")["claim_gate_passed"]
    with pytest.raises(ValueError, match="different inputs"):
        score(p, j, a, r, "changed-bytes")
    p["cases"].pop()
    with pytest.raises(ValueError, match="denominator"):
        score(p, j, a, r, "exact-bytes")


def test_semantic_match_alone_cannot_waive_grounding_or_broad_span():
    p, j, a, r = inputs()
    for case in p["cases"]:
        case["predictions"][0]["span"] = {"start_s": 0, "end_s": 30}
    result = score(p, j, a, r, "exact-bytes")
    assert result["content_recall"]["successes"] == 11
    assert result["grounded_recall"]["successes"] == 0
    assert not result["claim_gate_passed"]
    p["condition"] = j["condition"] = "issue-only"
    assert not score(p, j, a, r, "exact-bytes")["claim_gate_passed"]


def test_duplicate_gold_matches_and_truthy_string_judgments_are_rejected():
    p, j, a, r = inputs()
    p["cases"][0]["predictions"].append({"id": "duplicate", "span": {"start_s": 11, "end_s": 12}})
    j["predictions"].append({**j["predictions"][0], "prediction_id": "duplicate"})
    with pytest.raises(ValueError, match="multiply matched"):
        score(p, j, a, r, "exact-bytes")
    j["predictions"][0]["source_support"] = "false"
    with pytest.raises(ValueError, match="booleans"):
        score(p, j, a, r, "exact-bytes")
