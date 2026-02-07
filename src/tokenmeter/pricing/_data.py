"""Built-in pricing data for supported AI providers.

Prices are per million tokens (MTok) in USD.
Last updated: February 2026.
"""

from decimal import Decimal

# Anthropic pricing per million tokens
# Source: https://platform.claude.com/docs/en/about-claude/pricing
ANTHROPIC_PRICING: dict[str, dict[str, Decimal]] = {
    "claude-opus-4-6": {
        "input": Decimal("5.00"),
        "output": Decimal("25.00"),
        "cache_read": Decimal("0.50"),
        "cache_write_5m": Decimal("6.25"),
        "cache_write_1h": Decimal("10.00"),
        "batch_input": Decimal("2.50"),
        "batch_output": Decimal("12.50"),
    },
    "claude-opus-4-5": {
        "input": Decimal("5.00"),
        "output": Decimal("25.00"),
        "cache_read": Decimal("0.50"),
        "cache_write_5m": Decimal("6.25"),
        "cache_write_1h": Decimal("10.00"),
        "batch_input": Decimal("2.50"),
        "batch_output": Decimal("12.50"),
    },
    "claude-opus-4-1": {
        "input": Decimal("15.00"),
        "output": Decimal("75.00"),
        "cache_read": Decimal("1.50"),
        "cache_write_5m": Decimal("18.75"),
        "cache_write_1h": Decimal("30.00"),
        "batch_input": Decimal("7.50"),
        "batch_output": Decimal("37.50"),
    },
    "claude-opus-4": {
        "input": Decimal("15.00"),
        "output": Decimal("75.00"),
        "cache_read": Decimal("1.50"),
        "cache_write_5m": Decimal("18.75"),
        "cache_write_1h": Decimal("30.00"),
        "batch_input": Decimal("7.50"),
        "batch_output": Decimal("37.50"),
    },
    "claude-sonnet-4-5": {
        "input": Decimal("3.00"),
        "output": Decimal("15.00"),
        "cache_read": Decimal("0.30"),
        "cache_write_5m": Decimal("3.75"),
        "cache_write_1h": Decimal("6.00"),
        "batch_input": Decimal("1.50"),
        "batch_output": Decimal("7.50"),
    },
    "claude-sonnet-4": {
        "input": Decimal("3.00"),
        "output": Decimal("15.00"),
        "cache_read": Decimal("0.30"),
        "cache_write_5m": Decimal("3.75"),
        "cache_write_1h": Decimal("6.00"),
        "batch_input": Decimal("1.50"),
        "batch_output": Decimal("7.50"),
    },
    "claude-haiku-4-5": {
        "input": Decimal("1.00"),
        "output": Decimal("5.00"),
        "cache_read": Decimal("0.10"),
        "cache_write_5m": Decimal("1.25"),
        "cache_write_1h": Decimal("2.00"),
        "batch_input": Decimal("0.50"),
        "batch_output": Decimal("2.50"),
    },
    "claude-haiku-3-5": {
        "input": Decimal("0.80"),
        "output": Decimal("4.00"),
        "cache_read": Decimal("0.08"),
        "cache_write_5m": Decimal("1.00"),
        "cache_write_1h": Decimal("1.60"),
        "batch_input": Decimal("0.40"),
        "batch_output": Decimal("2.00"),
    },
    "claude-haiku-3": {
        "input": Decimal("0.25"),
        "output": Decimal("1.25"),
        "cache_read": Decimal("0.03"),
        "cache_write_5m": Decimal("0.30"),
        "cache_write_1h": Decimal("0.50"),
        "batch_input": Decimal("0.125"),
        "batch_output": Decimal("0.625"),
    },
}

# Common aliases for Anthropic models
ANTHROPIC_ALIASES: dict[str, str] = {
    "claude-opus-4-6-20250814": "claude-opus-4-6",
    "claude-opus-4-5-20250520": "claude-opus-4-5",
    "claude-sonnet-4-5-20250929": "claude-sonnet-4-5",
    "claude-sonnet-4-20250514": "claude-sonnet-4",
    "claude-haiku-4-5-20251001": "claude-haiku-4-5",
    "claude-3-5-haiku-20241022": "claude-haiku-3-5",
    "claude-3-haiku-20240307": "claude-haiku-3",
    "claude-3-opus-20240229": "claude-opus-4",
}

# OpenAI pricing per million tokens
# Source: https://openai.com/api/pricing/
OPENAI_PRICING: dict[str, dict[str, Decimal]] = {
    "gpt-5.1": {
        "input": Decimal("1.25"),
        "output": Decimal("10.00"),
        "cache_read": Decimal("0.125"),
    },
    "gpt-5.1-codex-mini": {
        "input": Decimal("0.25"),
        "output": Decimal("2.00"),
        "cache_read": Decimal("0.025"),
    },
    "gpt-5": {
        "input": Decimal("1.25"),
        "output": Decimal("10.00"),
        "cache_read": Decimal("0.125"),
    },
    "gpt-5-nano": {
        "input": Decimal("0.05"),
        "output": Decimal("0.40"),
        "cache_read": Decimal("0.005"),
    },
    "gpt-5-mini": {
        "input": Decimal("0.25"),
        "output": Decimal("2.00"),
        "cache_read": Decimal("0.025"),
    },
    "gpt-4.1": {
        "input": Decimal("2.00"),
        "output": Decimal("8.00"),
        "cache_read": Decimal("0.50"),
    },
    "gpt-4.1-mini": {
        "input": Decimal("0.40"),
        "output": Decimal("1.60"),
        "cache_read": Decimal("0.10"),
    },
    "gpt-4.1-nano": {
        "input": Decimal("0.10"),
        "output": Decimal("0.40"),
        "cache_read": Decimal("0.025"),
    },
    "gpt-4o": {
        "input": Decimal("2.50"),
        "output": Decimal("10.00"),
        "cache_read": Decimal("1.25"),
    },
    "gpt-4o-mini": {
        "input": Decimal("0.15"),
        "output": Decimal("0.60"),
        "cache_read": Decimal("0.075"),
    },
    "o3": {
        "input": Decimal("2.00"),
        "output": Decimal("8.00"),
        "cache_read": Decimal("0.50"),
    },
    "o3-mini": {
        "input": Decimal("1.10"),
        "output": Decimal("4.40"),
        "cache_read": Decimal("0.55"),
    },
    "o4-mini": {
        "input": Decimal("1.10"),
        "output": Decimal("4.40"),
        "cache_read": Decimal("0.275"),
    },
    "o1": {
        "input": Decimal("15.00"),
        "output": Decimal("60.00"),
        "cache_read": Decimal("7.50"),
    },
}

# Common aliases for OpenAI models
OPENAI_ALIASES: dict[str, str] = {
    "gpt-4o-2024-08-06": "gpt-4o",
    "gpt-4o-2024-11-20": "gpt-4o",
    "gpt-4o-mini-2024-07-18": "gpt-4o-mini",
    "chatgpt-4o-latest": "gpt-4o",
}
