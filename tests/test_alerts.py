from decimal import Decimal

import pytest

from tokenmeter.alerts import AlertManager
from tokenmeter.budget import BudgetManager
from tokenmeter.tracker import UsageTracker


@pytest.fixture
def tracker():
    return UsageTracker()


@pytest.fixture
def budget(tracker):
    return BudgetManager(tracker)


@pytest.fixture
def alerts(budget):
    return AlertManager(budget)


class TestAlertManager:
    def test_no_alerts_when_under_budget(self, alerts, budget):
        budget.set_budget(limit=100.00)
        messages = alerts.check_and_notify()
        assert len(messages) == 0

    def test_alerts_fire_when_threshold_crossed(self, alerts, budget, tracker):
        budget.set_budget(limit=0.01)
        alerts.set_thresholds([0.5, 1.0])
        # Record enough to cross both thresholds
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        messages = alerts.check_and_notify()
        assert len(messages) == 2

    def test_custom_callback(self, alerts, budget, tracker):
        received = []
        budget.set_budget(limit=0.01)
        alerts.set_thresholds([1.0])
        alerts.on_alert(lambda status, msg: received.append(msg))
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        alerts.check_and_notify()
        assert len(received) == 1
        assert "100%" in received[0]

    def test_threshold_only_fires_once(self, alerts, budget, tracker):
        budget.set_budget(limit=0.01)
        alerts.set_thresholds([0.5])
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        messages1 = alerts.check_and_notify()
        messages2 = alerts.check_and_notify()
        assert len(messages1) == 1
        assert len(messages2) == 0  # Already triggered

    def test_reset(self, alerts, budget, tracker):
        budget.set_budget(limit=0.01)
        alerts.set_thresholds([0.5])
        tracker.record_manual(model="claude-sonnet-4-5", input_tokens=100000, output_tokens=50000)
        alerts.check_and_notify()
        alerts.reset()
        messages = alerts.check_and_notify()
        assert len(messages) == 1  # Fires again after reset

    def test_set_thresholds(self, alerts):
        alerts.set_thresholds([0.25, 0.75])
        assert len(alerts._thresholds) == 2
        assert alerts._thresholds[0].percentage == 0.25
        assert alerts._thresholds[1].percentage == 0.75
