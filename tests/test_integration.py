"""End-to-end integration tests for the Meter facade."""

from decimal import Decimal

import pytest

import tokenmeter
from tests.conftest import make_anthropic_response, make_openai_response
from tokenmeter._types import BudgetExceededError


class TestMeterIntegration:
    def test_estimate_cost(self):
        meter = tokenmeter.Meter()
        cost = meter.estimate("Hello, how are you?", model="claude-sonnet-4-5")
        assert isinstance(cost, Decimal)
        assert cost > Decimal("0")

    def test_record_and_total(self):
        meter = tokenmeter.Meter()
        resp = make_anthropic_response(input_tokens=1000, output_tokens=500)
        record = meter.record(resp)
        assert record.total_cost > Decimal("0")
        assert meter.total() == record.total_cost

    def test_multiple_providers(self):
        meter = tokenmeter.Meter()
        meter.record(make_anthropic_response())
        meter.record(make_openai_response())
        summary = meter.summary(group_by="provider")
        assert "anthropic" in summary
        assert "openai" in summary
        assert meter.total() == sum(summary.values())

    def test_budget_workflow(self):
        meter = tokenmeter.Meter()
        meter.set_budget(limit=0.001, period="total", action="block")

        # Record usage that exceeds budget
        resp = make_anthropic_response(input_tokens=100000, output_tokens=50000)
        meter.record(resp)

        # Check budget
        statuses = meter.check_budget()
        assert len(statuses) == 1
        assert statuses[0].is_exceeded is True

        # Enforce should raise
        with pytest.raises(BudgetExceededError):
            meter.budget.enforce(Decimal("0.01"))

    def test_alert_workflow(self):
        meter = tokenmeter.Meter()
        meter.set_budget(limit=0.001)

        alerts_received = []
        meter.on_alert(lambda status, msg: alerts_received.append(msg))
        meter.alerts.set_thresholds([1.0])

        # Record usage that crosses threshold — alerts fire via record()
        resp = make_anthropic_response(input_tokens=100000, output_tokens=50000)
        meter.record(resp)

        assert len(alerts_received) == 1

    def test_tags_and_filtering(self):
        meter = tokenmeter.Meter()
        meter.record(make_anthropic_response(), feature="chat")
        meter.record(make_anthropic_response(), feature="search")
        meter.record(make_openai_response(), feature="chat")

        chat_total = meter.total(tags={"feature": "chat"})
        search_total = meter.total(tags={"feature": "search"})
        all_total = meter.total()

        assert chat_total > search_total  # 2 chat records vs 1 search
        assert chat_total + search_total == all_total

    def test_user_id_default(self):
        meter = tokenmeter.Meter(user_id="default-user")
        resp = make_anthropic_response()
        record = meter.record(resp)
        assert record.user_id == "default-user"

    def test_user_id_override(self):
        meter = tokenmeter.Meter(user_id="default-user")
        resp = make_anthropic_response()
        record = meter.record(resp, user_id="override-user")
        assert record.user_id == "override-user"

    def test_sqlite_storage(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        meter = tokenmeter.Meter(storage="sqlite", db_path=db_path)
        resp = make_anthropic_response(input_tokens=1000, output_tokens=500)
        record = meter.record(resp)
        assert meter.total() == record.total_cost

    def test_version(self):
        assert tokenmeter.__version__ == "0.1.0"

    def test_help(self, capsys):
        tokenmeter.help()
        captured = capsys.readouterr()
        assert "tokenmeter" in captured.out
        assert "QUICK START" in captured.out
        assert "BUDGETS" in captured.out
        assert "ALERTS" in captured.out
