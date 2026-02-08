# Cost Tracking

Calculate the cost of AI API calls using per-model pricing data.

## Classes

### `CostCalculator`

Stateless cost calculation engine. Source: `src/tokenmeter/cost.py`

```python
from tokenmeter import CostCalculator

calc = CostCalculator()
```

**Constructor:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pricing` | `PricingRegistry \| None` | `None` | Custom pricing registry (uses built-in if omitted) |

**Methods:**

#### `calculate(model, input_tokens, output_tokens, cache_read_tokens=0, cache_write_tokens=0) -> Decimal`

Returns total cost in USD.

```python
cost = calc.calculate(model="gpt-4o", input_tokens=1500, output_tokens=500)
# Decimal('0.00875')
```

#### `calculate_detailed(model, input_tokens, output_tokens, cache_read_tokens=0, cache_write_tokens=0) -> dict`

Returns itemized breakdown:

```python
details = calc.calculate_detailed(model="claude-opus-4-6", input_tokens=10000, output_tokens=5000)
# {
#     "input_cost": Decimal("0.05"),
#     "output_cost": Decimal("0.125"),
#     "cache_read_cost": Decimal("0"),
#     "cache_write_cost": Decimal("0"),
#     "total_cost": Decimal("0.175"),
# }
```

#### `estimate_input_cost(text, model) -> Decimal`

Heuristic-based estimate (~4 chars per token) without an API call.

```python
cost = calc.estimate_input_cost("Hello, how are you?", model="claude-sonnet-4-5")
```

### `PricingRegistry`

Manages per-model pricing data. Source: `src/tokenmeter/pricing/__init__.py`

```python
from tokenmeter import PricingRegistry

registry = PricingRegistry()
```

**Methods:**

#### `get(model) -> ModelPricing`

Look up pricing. Raises `UnknownModelError` if not found. Resolves aliases automatically (e.g., `"claude-sonnet-4-5-20250929"` -> `"claude-sonnet-4-5"`).

```python
pricing = registry.get("claude-sonnet-4-5")
print(pricing.input_per_mtok)   # Decimal('3.00')
print(pricing.output_per_mtok)  # Decimal('15.00')
```

#### `register(pricing: ModelPricing)`

Register custom model pricing:

```python
from tokenmeter._types import ModelPricing
from decimal import Decimal

registry.register(ModelPricing(
    model_id="my-model",
    provider="custom",
    input_per_mtok=Decimal("1.00"),
    output_per_mtok=Decimal("5.00"),
))
```

#### `add_alias(alias, model_id)`

Map an alias to an existing model ID:

```python
registry.add_alias("my-model-v2", "my-model")
```

#### `list_models(provider=None) -> list[str]`

List all known model IDs, optionally filtered by provider.

### `ModelPricing`

Frozen dataclass for per-model pricing. Source: `src/tokenmeter/_types.py`

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | `str` | Model identifier |
| `provider` | `str` | Provider name (e.g., `"anthropic"`, `"openai"`) |
| `input_per_mtok` | `Decimal` | USD per million input tokens |
| `output_per_mtok` | `Decimal` | USD per million output tokens |
| `cache_read_per_mtok` | `Decimal \| None` | USD per million cache read tokens |
| `cache_write_per_mtok` | `Decimal \| None` | USD per million cache write tokens |
| `batch_input_per_mtok` | `Decimal \| None` | USD per million batch input tokens |
| `batch_output_per_mtok` | `Decimal \| None` | USD per million batch output tokens |

## Built-in Models

**Anthropic:** claude-opus-4-6, claude-opus-4-5, claude-opus-4-1, claude-opus-4, claude-sonnet-4-5, claude-sonnet-4, claude-haiku-4-5, claude-haiku-3-5, claude-haiku-3

**OpenAI:** gpt-5.1, gpt-5.1-codex-mini, gpt-5, gpt-5-mini, gpt-5-nano, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, gpt-4o, gpt-4o-mini, o3, o3-mini, o4-mini, o1

Pricing data is in `src/tokenmeter/pricing/_data.py`.

## Notes

- All monetary values use `Decimal` for precision — never `float`.
- Cost = `(tokens / 1,000,000) * price_per_mtok` for each token type.
- Cache tokens with `None` pricing are treated as zero cost.
