import uuid
from datetime import datetime
from decimal import Decimal

import pytest

from tokenmeter._types import UsageRecord
from tokenmeter.storage.memory import MemoryStorage


def _make_record(**kwargs):
    defaults = dict(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(),
        provider="anthropic",
        model="claude-sonnet-4-5",
        input_tokens=100,
        output_tokens=50,
        input_cost=Decimal("0.0003"),
        output_cost=Decimal("0.00075"),
        total_cost=Decimal("0.00105"),
    )
    defaults.update(kwargs)
    return UsageRecord(**defaults)


class TestMemoryStorage:
    def test_save_and_query(self):
        storage = MemoryStorage()
        record = _make_record()
        storage.save(record)
        results = storage.query()
        assert len(results) == 1
        assert results[0].id == record.id

    def test_query_by_provider(self):
        storage = MemoryStorage()
        storage.save(_make_record(provider="anthropic"))
        storage.save(_make_record(provider="openai"))
        results = storage.query(provider="anthropic")
        assert len(results) == 1

    def test_query_by_model(self):
        storage = MemoryStorage()
        storage.save(_make_record(model="claude-sonnet-4-5"))
        storage.save(_make_record(model="gpt-4o"))
        results = storage.query(model="gpt-4o")
        assert len(results) == 1

    def test_query_by_user_id(self):
        storage = MemoryStorage()
        storage.save(_make_record(user_id="alice"))
        storage.save(_make_record(user_id="bob"))
        results = storage.query(user_id="alice")
        assert len(results) == 1

    def test_query_by_tags(self):
        storage = MemoryStorage()
        storage.save(_make_record(tags={"env": "prod"}))
        storage.save(_make_record(tags={"env": "staging"}))
        results = storage.query(tags={"env": "prod"})
        assert len(results) == 1

    def test_clear(self):
        storage = MemoryStorage()
        storage.save(_make_record())
        storage.save(_make_record())
        storage.clear()
        assert len(storage.query()) == 0
