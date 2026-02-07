from __future__ import annotations

from typing import Any

from tokenmeter.providers._base import Provider
from tokenmeter.providers.anthropic import AnthropicProvider
from tokenmeter.providers.openai import OpenAIProvider


class ProviderRegistry:
    """Registry for AI provider integrations with auto-detection."""

    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        anthropic = AnthropicProvider()
        openai = OpenAIProvider()
        self._providers[anthropic.name] = anthropic
        self._providers[openai.name] = openai

    def register(self, provider: Provider) -> None:
        """Register a custom provider."""
        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        """Get a provider by name. Raises KeyError if not found."""
        return self._providers[name]

    def detect(self, response: Any) -> Provider:
        """Auto-detect provider from a response object.

        Raises ValueError if no provider matches.
        """
        for provider in self._providers.values():
            if provider.matches_response(response):
                return provider
        raise ValueError(
            f"Could not detect provider for response type {type(response).__qualname__}. "
            "Register a custom provider with ProviderRegistry.register()."
        )

    def list_providers(self) -> list[str]:
        return list(self._providers.keys())
