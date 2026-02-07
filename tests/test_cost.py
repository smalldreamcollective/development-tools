from decimal import Decimal

import pytest

from tokenmeter._types import UnknownModelError
from tokenmeter.cost import CostCalculator


@pytest.fixture
def calc():
    return CostCalculator()


class TestCostCalculator:
    def test_basic_calculation(self, calc):
        # claude-sonnet-4-5: $3/MTok input, $15/MTok output
        cost = calc.calculate("claude-sonnet-4-5", input_tokens=1000, output_tokens=500)
        expected_input = Decimal("1000") / Decimal("1000000") * Decimal("3.00")
        expected_output = Decimal("500") / Decimal("1000000") * Decimal("15.00")
        assert cost == expected_input + expected_output

    def test_zero_tokens(self, calc):
        cost = calc.calculate("claude-sonnet-4-5", input_tokens=0, output_tokens=0)
        assert cost == Decimal("0")

    def test_with_cache_tokens(self, calc):
        cost = calc.calculate(
            "claude-sonnet-4-5",
            input_tokens=1000,
            output_tokens=500,
            cache_read_tokens=200,
        )
        assert cost > Decimal("0")

    def test_unknown_model_raises(self, calc):
        with pytest.raises(UnknownModelError):
            calc.calculate("nonexistent-model", input_tokens=100, output_tokens=50)

    def test_calculate_detailed(self, calc):
        result = calc.calculate_detailed(
            "gpt-4o", input_tokens=1000000, output_tokens=1000000
        )
        assert result["input_cost"] == Decimal("2.50")
        assert result["output_cost"] == Decimal("10.00")
        assert result["total_cost"] == Decimal("12.50")

    def test_estimate_input_cost(self, calc):
        cost = calc.estimate_input_cost("Hello world, this is a test.", model="claude-haiku-4-5")
        assert cost > Decimal("0")
        assert isinstance(cost, Decimal)

    def test_openai_pricing(self, calc):
        # gpt-4.1: $2/MTok input, $8/MTok output
        cost = calc.calculate("gpt-4.1", input_tokens=1000000, output_tokens=1000000)
        assert cost == Decimal("10.00")

    def test_decimal_precision(self, calc):
        # Verify no floating point errors accumulate
        cost = calc.calculate("claude-sonnet-4-5", input_tokens=1, output_tokens=1)
        assert isinstance(cost, Decimal)
        # Should be exact, not a float approximation
        expected = Decimal("1") / Decimal("1000000") * Decimal("3.00") + \
                   Decimal("1") / Decimal("1000000") * Decimal("15.00")
        assert cost == expected
