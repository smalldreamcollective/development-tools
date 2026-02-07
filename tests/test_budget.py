from decimal import Decimal

import pytest

from tokenmeter._types import BudgetExceededError
from tokenmeter.budget import BudgetManager
from tokenmeter.tracker import UsageTracker


@pytest.fixture
def tracker():
    return UsageTracker()


@pytest.fixture
def budget(tracker):
    return BudgetManager(tracker)


class TestBudgetManager:
    def test_set_budget(self, budget):
        config = budget.set_budget(limit=10.00, period="daily")
        assert config.limit == Decimal("10.00")
        assert config.period == "daily"
        assert config.action == "warn"

    def test_check_empty(self, budget):
        budget.set_budget(limit=10.00)
        statuses = budget.check()
        assert len(statuses) == 1
        assert statuses[0].spent == Decimal("0")
        assert statuses[0].remaining == Decimal("10.00")
        assert statuses[0].is_exceeded is False

    def test_check_with_usage(self, budget, tracker):
        budget.set_budget(limit=1.00)
        # Record some usage manually
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        statuses = budget.check()
        assert statuses[0].spent > Decimal("0")

    def test_would_exceed_false(self, budget):
        budget.set_budget(limit=10.00)
        assert budget.would_exceed(Decimal("5.00")) is False

    def test_would_exceed_true(self, budget, tracker):
        budget.set_budget(limit=0.01)
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        assert budget.would_exceed(Decimal("0.01")) is True

    def test_enforce_no_block(self, budget, tracker):
        # action="warn" should not raise
        budget.set_budget(limit=0.001, action="warn")
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        # Should not raise even though exceeded
        budget.enforce(Decimal("1.00"))

    def test_enforce_block_raises(self, budget, tracker):
        budget.set_budget(limit=0.001, action="block")
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        with pytest.raises(BudgetExceededError):
            budget.enforce(Decimal("1.00"))

    def test_remove_budget(self, budget):
        config = budget.set_budget(limit=10.00)
        assert len(budget.list_budgets()) == 1
        budget.remove_budget(config)
        assert len(budget.list_budgets()) == 0

    def test_multiple_budgets(self, budget):
        budget.set_budget(limit=10.00, period="daily")
        budget.set_budget(limit=100.00, period="monthly")
        assert len(budget.list_budgets()) == 2
        statuses = budget.check()
        assert len(statuses) == 2
