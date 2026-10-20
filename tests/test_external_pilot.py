"""Protect the admission checks for a failure-only upstream test reporter."""

import importlib.util
import json
from pathlib import Path
import pytest


spec = importlib.util.spec_from_file_location(
    "external_pilot", Path(__file__).resolve().parents[1] / "scripts/pilot_swebench_task.py"
)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


def test_browser_never_started_is_not_positive_completion():
    result = pilot.evidence("Executed 0 of 0\nTOTAL: 0 SUCCESS\nSVH_TEST_EXIT_CODE:0\n", "color")
    assert not result["suite_complete"]
    assert not result["all_passed"]


def test_incomplete_or_skipped_suite_is_not_complete():
    result = pilot.evidence("Executed 1 of 2\nTOTAL: 1 SUCCESS\nSVH_TEST_EXIT_CODE:0\n", "color")
    assert not result["suite_complete"]


def test_existing_skips_are_explicitly_accounted_for():
    result = pilot.evidence("Executed 2 of 3 (skipped 1)\nTOTAL: 2 SUCCESS\n", "color")
    assert result["suite_complete"]
    assert result["executed"] == 2 and result["discovered"] == 3 and result["skipped"] == 1


def test_fail_only_report_requires_the_specific_test():
    log = (
        "\x1b[1A\x1b[2KChrome Headless 131.0.0.0 (Linux x86_64) color FAILED\n"
        "AssertionError: expected red to equal blue\n"
        "Executed 2 of 2 (1 FAILED)\nTOTAL: 1 FAILED, 1 SUCCESS\nSVH_TEST_EXIT_CODE:1\n"
    )
    result = pilot.evidence(log, "color")
    assert result["suite_complete"]
    assert result["expected_failure_observed"]
    assert result["assertion_observed"]
    assert not result["all_passed"]
    assert pilot.evidence(log, "color ")["expected_failure_observed"]
    assert not pilot.evidence(log, "different test")["expected_failure_observed"]


def test_pass_requires_a_positive_suite_summary():
    log = "Executed 2 of 2 SUCCESS\nTOTAL: 2 SUCCESS\nSVH_TEST_EXIT_CODE:0\n"
    result = pilot.evidence(log, "color")
    assert result["suite_complete"] and result["all_passed"]
    assert result["test_exit_code"] == 0
    assert not pilot.evidence("SVH_TEST_EXIT_CODE:0\n", "color")["all_passed"]


def test_another_tests_assertion_cannot_validate_target_crash():
    log = (
        "Chrome Headless 131.0.0.0 (Linux x86_64) target FAILED\nTypeError: setup failed\n"
        "Chrome Headless 131.0.0.0 (Linux x86_64) other FAILED\nAssertionError: different bug\n"
    )
    assert not pilot.evidence(log, "target")["assertion_observed"]
    assert not pilot.evidence(log, ["target", "other"])["assertion_observed"]


@pytest.mark.parametrize("side,key,value", [
    ("pre", "expected_failure_observed", False),
    ("pre", "assertion_observed", False),
    ("pre", "test_exit_code", 0),
    ("post", "suite_complete", False),
    ("post", "skipped", 8),
    ("post", "all_passed", False),
    ("post", "base_commit_observed", "0" * 40),
])
def test_evidence_cannot_be_promoted_with_broken_integrity(side, key, value):
    report = json.loads((Path(__file__).resolve().parents[1] / "notes/runs/swebench-bpmn-pilot.json").read_text())
    pre, post = report["results"]["pre"], report["results"]["post"]
    assert pilot.verified_pair(pre, post, report["base_commit"])
    report["results"][side][key] = value
    assert not pilot.verified_pair(pre, post, report["base_commit"])
