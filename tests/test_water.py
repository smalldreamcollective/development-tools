"""Tests for water estimation: calculator, registry, and profiles."""

from decimal import Decimal

import pytest

from tokenmeter._types import ModelWaterProfile, WaterProfile
from tokenmeter.water import WaterRegistry
from tokenmeter.water.calculator import WaterCalculator


class TestWaterRegistry:
    def test_builtins_loaded(self):
        registry = WaterRegistry()
        profile = registry.get("claude-sonnet-4-5")
        assert profile is not None
        assert profile.energy_per_mtok == Decimal("450")

    def test_unknown_returns_none(self):
        registry = WaterRegistry()
        assert registry.get("unknown-model-xyz") is None

    def test_custom_registration(self):
        registry = WaterRegistry()
        custom = ModelWaterProfile(
            model_id="my-model", provider="custom", energy_per_mtok=Decimal("200")
        )
        registry.register(custom)
        result = registry.get("my-model")
        assert result is not None
        assert result.energy_per_mtok == Decimal("200")

    def test_aliases(self):
        registry = WaterRegistry()
        # Anthropic alias should resolve
        profile = registry.get("claude-sonnet-4-5-20250929")
        assert profile is not None
        assert profile.model_id == "claude-sonnet-4-5"

    def test_list_models(self):
        registry = WaterRegistry()
        all_models = registry.list_models()
        assert len(all_models) > 0
        anthropic_models = registry.list_models(provider="anthropic")
        openai_models = registry.list_models(provider="openai")
        assert len(anthropic_models) + len(openai_models) == len(all_models)


class TestWaterCalculator:
    def test_basic_calculation(self):
        calc = WaterCalculator()
        water = calc.calculate(
            model="claude-sonnet-4-5", input_tokens=500, output_tokens=500
        )
        assert water > Decimal("0")

    def test_zero_tokens(self):
        calc = WaterCalculator()
        water = calc.calculate(
            model="claude-sonnet-4-5", input_tokens=0, output_tokens=0
        )
        assert water == Decimal("0")

    def test_unknown_model_returns_zero(self):
        calc = WaterCalculator()
        water = calc.calculate(
            model="unknown-model-xyz", input_tokens=1000, output_tokens=500
        )
        assert water == Decimal("0")

    def test_custom_profile(self):
        profile = WaterProfile(
            pue=Decimal("1.1"),
            wue_site=Decimal("1.5"),
            wue_source=Decimal("0.4"),
        )
        calc = WaterCalculator(profile=profile)
        water_custom = calc.calculate(
            model="claude-sonnet-4-5", input_tokens=1000, output_tokens=0
        )
        calc_default = WaterCalculator()
        water_default = calc_default.calculate(
            model="claude-sonnet-4-5", input_tokens=1000, output_tokens=0
        )
        # Different profiles should give different results
        assert water_custom != water_default

    def test_cache_tokens_contribute(self):
        calc = WaterCalculator()
        water_no_cache = calc.calculate(
            model="claude-sonnet-4-5", input_tokens=1000, output_tokens=0
        )
        water_with_cache = calc.calculate(
            model="claude-sonnet-4-5",
            input_tokens=1000,
            output_tokens=0,
            cache_read_tokens=500,
            cache_write_tokens=500,
        )
        assert water_with_cache > water_no_cache

    def test_decimal_precision(self):
        calc = WaterCalculator()
        water = calc.calculate(
            model="claude-sonnet-4-5", input_tokens=1, output_tokens=0
        )
        assert isinstance(water, Decimal)
        assert water > Decimal("0")

    def test_estimate_input_water(self):
        calc = WaterCalculator()
        water = calc.estimate_input_water("Hello, world!", model="claude-sonnet-4-5")
        assert water > Decimal("0")

    def test_formula_correctness(self):
        """Verify the formula: water_mL = (tokens / 1M) * energy_wh / 1000 * (wue_site / pue + wue_source) * 1000"""
        profile = WaterProfile(
            pue=Decimal("1.2"),
            wue_site=Decimal("1.8"),
            wue_source=Decimal("0.5"),
        )
        calc = WaterCalculator(profile=profile)
        # 1M tokens of claude-sonnet-4-5 (450 Wh/MTok)
        water = calc.calculate(
            model="claude-sonnet-4-5", input_tokens=1_000_000, output_tokens=0
        )
        # Manual: (1M / 1M) * 450 / 1000 * (1.8 / 1.2 + 0.5) * 1000
        #       = 1 * 0.45 * (1.5 + 0.5) * 1000
        #       = 0.45 * 2.0 * 1000
        #       = 900 mL
        assert water == Decimal("900")
