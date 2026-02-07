from decimal import Decimal

import pytest

from tests.conftest import make_anthropic_response, make_openai_response
from tokenmeter.tracker import UsageTracker


@pytest.fixture
def tracker():
    return UsageTracker()


class TestUsageTracker:
    def test_record_anthropic_response(self, tracker):
        resp = make_anthropic_response(input_tokens=1000, output_tokens=500)
        record = tracker.record(resp)
        assert record.provider == "anthropic"
        assert record.model == "claude-sonnet-4-5"
        assert record.input_tokens == 1000
        assert record.output_tokens == 500
        assert record.total_cost > Decimal("0")

    def test_record_openai_response(self, tracker):
        resp = make_openai_response(prompt_tokens=1000, completion_tokens=500)
        record = tracker.record(resp)
        assert record.provider == "openai"
        assert record.model == "gpt-4o"
        assert record.input_tokens == 1000
        assert record.output_tokens == 500
        assert record.total_cost > Decimal("0")

    def test_record_manual(self, tracker):
        record = tracker.record_manual(
            model="claude-sonnet-4-5",
            input_tokens=1000,
            output_tokens=500,
        )
        assert record.provider == "anthropic"
        assert record.total_cost > Decimal("0")

    def test_get_total(self, tracker):
        resp1 = make_anthropic_response(input_tokens=1000, output_tokens=500)
        resp2 = make_anthropic_response(input_tokens=2000, output_tokens=1000)
        r1 = tracker.record(resp1)
        r2 = tracker.record(resp2)
        total = tracker.get_total()
        assert total == r1.total_cost + r2.total_cost

    def test_get_total_filtered(self, tracker):
        tracker.record(make_anthropic_response())
        tracker.record(make_openai_response())
        anthropic_total = tracker.get_total(provider="anthropic")
        openai_total = tracker.get_total(provider="openai")
        all_total = tracker.get_total()
        assert anthropic_total + openai_total == all_total

    def test_get_summary_by_model(self, tracker):
        tracker.record(make_anthropic_response())
        tracker.record(make_openai_response())
        summary = tracker.get_summary(group_by="model")
        assert "claude-sonnet-4-5" in summary
        assert "gpt-4o" in summary

    def test_get_summary_by_provider(self, tracker):
        tracker.record(make_anthropic_response())
        tracker.record(make_openai_response())
        summary = tracker.get_summary(group_by="provider")
        assert "anthropic" in summary
        assert "openai" in summary

    def test_tags(self, tracker):
        tracker.record(make_anthropic_response(), feature="chat")
        tracker.record(make_anthropic_response(), feature="search")
        chat_total = tracker.get_total(tags={"feature": "chat"})
        assert chat_total > Decimal("0")
        search_total = tracker.get_total(tags={"feature": "search"})
        assert search_total > Decimal("0")

    def test_user_id(self, tracker):
        tracker.record(make_anthropic_response(), user_id="alice")
        tracker.record(make_anthropic_response(), user_id="bob")
        alice_total = tracker.get_total(user_id="alice")
        bob_total = tracker.get_total(user_id="bob")
        assert alice_total > Decimal("0")
        assert bob_total > Decimal("0")
        assert alice_total == bob_total  # same tokens, same model

    def test_session_id(self, tracker):
        assert tracker.session_id  # auto-generated
        records = tracker.get_records(session_id=tracker.session_id)
        # No records yet
        assert len(records) == 0
        tracker.record(make_anthropic_response())
        records = tracker.get_records(session_id=tracker.session_id)
        assert len(records) == 1
