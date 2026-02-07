from __future__ import annotations

import threading
from datetime import datetime

from tokenmeter._types import UsageRecord
from tokenmeter.storage._base import StorageBackend


class MemoryStorage(StorageBackend):
    """In-memory storage backend. Fast, zero-config, lost on process exit."""

    def __init__(self) -> None:
        self._records: list[UsageRecord] = []
        self._lock = threading.Lock()

    def save(self, record: UsageRecord) -> None:
        with self._lock:
            self._records.append(record)

    def query(
        self,
        provider: str | None = None,
        model: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        tags: dict[str, str] | None = None,
    ) -> list[UsageRecord]:
        with self._lock:
            results = list(self._records)

        if provider is not None:
            results = [r for r in results if r.provider == provider]
        if model is not None:
            results = [r for r in results if r.model == model]
        if user_id is not None:
            results = [r for r in results if r.user_id == user_id]
        if session_id is not None:
            results = [r for r in results if r.session_id == session_id]
        if since is not None:
            results = [r for r in results if r.timestamp >= since]
        if until is not None:
            results = [r for r in results if r.timestamp <= until]
        if tags is not None:
            results = [
                r for r in results if all(r.tags.get(k) == v for k, v in tags.items())
            ]
        return results

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
