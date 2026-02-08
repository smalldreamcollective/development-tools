from __future__ import annotations

from decimal import Decimal

from tokenmeter._types import WaterProfile
from tokenmeter.water import WaterRegistry

_ONE_MILLION = Decimal("1000000")
_ONE_THOUSAND = Decimal("1000")


class WaterCalculator:
    """Estimates water usage (mL) for AI model inference."""

    def __init__(
        self,
        registry: WaterRegistry | None = None,
        profile: WaterProfile | None = None,
    ) -> None:
        self._registry = registry or WaterRegistry()
        self._profile = profile or WaterProfile()

    def calculate(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cache_read_tokens: int = 0,
        cache_write_tokens: int = 0,
    ) -> Decimal:
        """Calculate estimated water usage in mL. Returns 0 if model unknown."""
        water_profile = self._registry.get(model)
        if water_profile is None:
            return Decimal("0")

        total_tokens = input_tokens + output_tokens + cache_read_tokens + cache_write_tokens
        if total_tokens <= 0:
            return Decimal("0")

        # water_mL = (tokens / 1M) * energy_wh_per_mtok / 1000 * (wue_site / pue + wue_source) * 1000
        tokens_in_millions = Decimal(total_tokens) / _ONE_MILLION
        energy_kwh = tokens_in_millions * water_profile.energy_per_mtok / _ONE_THOUSAND
        water_factor = self._profile.wue_site / self._profile.pue + self._profile.wue_source
        water_liters = energy_kwh * water_factor
        water_ml = water_liters * _ONE_THOUSAND
        return water_ml

    def estimate_input_water(self, text: str, model: str) -> Decimal:
        """Estimate water usage for sending text as input, using ~4 chars per token heuristic."""
        estimated_tokens = max(1, len(text) // 4)
        return self.calculate(model=model, input_tokens=estimated_tokens, output_tokens=0)
