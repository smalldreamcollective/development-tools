from __future__ import annotations

from typing import Any

from tokenmeter.providers import ProviderRegistry


class TokenCounter:
    """Token counting using provider-specific tokenizers or heuristics."""

    def __init__(self, providers: ProviderRegistry | None = None) -> None:
        self._providers = providers or ProviderRegistry()

    def count_local(self, text: str, model: str, provider: str | None = None) -> int:
        """Count tokens locally using the best available tokenizer.

        If provider is not specified, tries to infer from the model name.
        """
        provider_name = provider or _infer_provider(model)
        prov = self._providers.get(provider_name)
        return prov.count_tokens_local(text, model)

    def count_messages_local(
        self, messages: list[dict[str, str]], model: str, provider: str | None = None
    ) -> int:
        """Count tokens for a list of chat messages.

        Adds per-message overhead (~4 tokens per message for role/formatting).
        """
        provider_name = provider or _infer_provider(model)
        prov = self._providers.get(provider_name)
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            total += prov.count_tokens_local(content, model)
            total += 4  # approximate overhead per message (role, delimiters)
        total += 3  # priming tokens
        return total

    def from_response(self, response: Any) -> dict[str, int]:
        """Extract actual token usage from an API response."""
        prov = self._providers.detect(response)
        return prov.extract_usage(response)


def _infer_provider(model: str) -> str:
    """Infer provider name from model string."""
    model_lower = model.lower()
    if "claude" in model_lower:
        return "anthropic"
    if any(prefix in model_lower for prefix in ("gpt", "o1", "o3", "o4")):
        return "openai"
    raise ValueError(
        f"Cannot infer provider for model {model!r}. Pass provider='...' explicitly."
    )
