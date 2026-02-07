from __future__ import annotations

from decimal import Decimal

from tokenmeter._types import ModelPricing
from tokenmeter.pricing import PricingRegistry

_ONE_MILLION = Decimal("1000000")


class CostCalculator:
    """Stateless cost calculation engine."""

    def __init__(self, pricing: PricingRegistry | None = None) -> None:
        self._pricing = pricing or PricingRegistry()

    def calculate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> Decimal:
        """Calculate total cost in USD for given token usage."""
        pricing = self._pricing.get(model)
        return self._compute(pricing, input_tokens, output_tokens, cache_read_tokens, cache_write_tokens)

    def calculate_detailed(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> dict[str, Decimal]:
        """Calculate itemized costs. Returns dict with input_cost, output_cost, cache_read_cost, cache_write_cost, total_cost."""
        pricing = self._pricing.get(model)
        input_cost = _tokens_to_cost(input_tokens, pricing.input_per_mtok)
        output_cost = _tokens_to_cost(output_tokens, pricing.output_per_mtok)
        cache_read_cost = _tokens_to_cost(cache_read_tokens, pricing.cache_read_per_mtok)
        cache_write_cost = _tokens_to_cost(cache_write_tokens, pricing.cache_write_per_mtok)
        total = input_cost + output_cost + cache_read_cost + cache_write_cost
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "cache_read_cost": cache_read_cost,
            "cache_write_cost": cache_write_cost,
            "total_cost": total,
        }

    def estimate_input_cost(self, text: str, model: str) -> Decimal:
        """Estimate cost of sending text as input, using ~4 chars per token heuristic."""
        estimated_tokens = max(1, len(text) // 4)
        pricing = self._pricing.get(model)
        return _tokens_to_cost(estimated_tokens, pricing.input_per_mtok)

    @staticmethod
    def _compute(
        pricing: ModelPricing,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int,
        cache_write_tokens: int,
    ) -> Decimal:
        total = Decimal("0")
        total += _tokens_to_cost(input_tokens, pricing.input_per_mtok)
        total += _tokens_to_cost(output_tokens, pricing.output_per_mtok)
        total += _tokens_to_cost(cache_read_tokens, pricing.cache_read_per_mtok)
        total += _tokens_to_cost(cache_write_tokens, pricing.cache_write_per_mtok)
        return total


def _tokens_to_cost(tokens: int, price_per_mtok: Decimal | None) -> Decimal:
    if tokens <= 0 or price_per_mtok is None:
        return Decimal("0")
    return (Decimal(tokens) / _ONE_MILLION) * price_per_mtok
