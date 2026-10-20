from concurrent.futures import ThreadPoolExecutor

import pytest

from svh.budget import Budget, BudgetExceeded, microdollars, token_cost


def test_costs_round_up_and_reject_invalid_values():
    assert microdollars("0.0000001") == 1
    assert token_cost(1, 1, "0.75", "3.75") == 5
    for bad in ["NaN", "Infinity", -1]:
        with pytest.raises(ValueError):
            microdollars(bad)
    with pytest.raises(ValueError):
        token_cost(1.5, 1, 1, 1)


def test_ambiguous_outcome_survives_restart_and_higher_config_cap(tmp_path):
    path = tmp_path / "ledger.db"
    first = Budget(path, "0.01")
    first.reserve(8_000, label="timeout-with-unknown-charge")
    resumed = Budget(path, "100")
    with pytest.raises(BudgetExceeded):
        resumed.reserve(2_001, label="would-overrun")
    assert resumed.summary()["unsettled_requests"] == 1
    assert resumed.summary()["cap_microdollars"] == 10_000


def test_concurrent_reservations_cannot_overrun(tmp_path):
    budget = Budget(tmp_path / "ledger.db", "0.01")

    def attempt(_):
        try:
            return budget.reserve(1_000, label="parallel-request")
        except BudgetExceeded:
            return None

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(attempt, range(30)))
    assert sum(value is not None for value in results) == 10
    assert budget.summary()["available_microdollars"] == 0


def test_only_settled_cost_releases_reservation_and_settlement_is_idempotent(tmp_path):
    budget = Budget(tmp_path / "ledger.db", "0.01")
    request = budget.reserve(10_000, label="known-metered-result")
    budget.settle(request, 2_000)
    budget.settle(request, 2_000)
    assert budget.summary()["available_microdollars"] == 8_000
    with pytest.raises(ValueError):
        budget.settle(request, 1_000)


def test_unexpected_overage_is_recorded_and_disables_future_calls(tmp_path):
    budget = Budget(tmp_path / "ledger.db", "1")
    request = budget.reserve(1_000, label="incorrect-bound")
    with pytest.raises(BudgetExceeded):
        budget.settle(request, 2_000)
    assert budget.summary()["charged_or_reserved_microdollars"] == 2_000
    with pytest.raises(BudgetExceeded):
        budget.reserve(1, label="disabled")
