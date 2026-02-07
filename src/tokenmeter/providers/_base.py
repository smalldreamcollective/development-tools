from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Provider(ABC):
    """Base class for AI provider integrations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier, e.g. 'anthropic', 'openai'."""

    @abstractmethod
    def count_tokens_local(self, text: str, model: str) -> int:
        """Estimate token count locally without an API call.

        Returns best-effort estimate. May use heuristic if tokenizer unavailable.
        """

    @abstractmethod
    def extract_usage(self, response: Any) -> dict[str, int]:
        """Extract token usage from a provider API response object.

        Returns dict with keys: input_tokens, output_tokens,
        and optionally cache_read_tokens, cache_write_tokens.
        """

    @abstractmethod
    def extract_model(self, response: Any) -> str:
        """Extract the model identifier from a provider API response."""

    @abstractmethod
    def matches_response(self, response: Any) -> bool:
        """Return True if this provider can handle the given response object."""
