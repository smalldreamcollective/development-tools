from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from tokenmeter._types import UsageRecord


class StorageBackend(ABC):
    """Abstract base class for usage record storage."""

    @abstractmethod
    def save(self, record: UsageRecord) -> None:
        """Persist a single usage record."""

    @abstractmethod
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
        """Query records matching the given filters."""

    @abstractmethod
    def clear(self) -> None:
        """Delete all stored records."""
