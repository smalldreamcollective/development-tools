from __future__ import annotations

from decimal import Decimal

from tokenmeter._types import ModelPricing, UnknownModelError
from tokenmeter.pricing._data import (
    ANTHROPIC_ALIASES,
    ANTHROPIC_PRICING,
    OPENAI_ALIASES,
    OPENAI_PRICING,
)


class PricingRegistry:
    """Central registry for model pricing. Supports built-in and custom pricing."""

    def __init__(self) -> None:
        self._models: dict[str, ModelPricing] = {}
        self._aliases: dict[str, str] = {}
        self._load_builtin()

    def _load_builtin(self) -> None:
        for model_id, prices in ANTHROPIC_PRICING.items():
            self._models[model_id] = _dict_to_pricing(model_id, "anthropic", prices)
        for model_id, prices in OPENAI_PRICING.items():
            self._models[model_id] = _dict_to_pricing(model_id, "openai", prices)
        self._aliases.update(ANTHROPIC_ALIASES)
        self._aliases.update(OPENAI_ALIASES)

    def get(self, model: str) -> ModelPricing:
        """Look up pricing for a model. Raises UnknownModelError if not found."""
        resolved = self._resolve(model)
        if resolved not in self._models:
            raise UnknownModelError(model)
        return self._models[resolved]

    def register(self, pricing: ModelPricing) -> None:
        """Register or override pricing for a model."""
        self._models[pricing.model_id] = pricing

    def add_alias(self, alias: str, model_id: str) -> None:
        """Add an alias that maps to an existing model ID."""
        self._aliases[alias] = model_id

    def list_models(self, provider: str | None = None) -> list[str]:
        """List all known model IDs, optionally filtered by provider."""
        if provider is None:
            return list(self._models.keys())
        return [m for m, p in self._models.items() if p.provider == provider]

    def _resolve(self, model: str) -> str:
        """Resolve aliases and normalize model strings."""
        normalized = model.lower().strip()
        return self._aliases.get(normalized, normalized)


def _dict_to_pricing(model_id: str, provider: str, prices: dict[str, Decimal]) -> ModelPricing:
    return ModelPricing(
        model_id=model_id,
        provider=provider,
        input_per_mtok=prices["input"],
        output_per_mtok=prices["output"],
        cache_read_per_mtok=prices.get("cache_read"),
        cache_write_per_mtok=prices.get("cache_write_5m"),
        batch_input_per_mtok=prices.get("batch_input"),
        batch_output_per_mtok=prices.get("batch_output"),
    )
