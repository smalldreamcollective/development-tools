# Water Estimation

Estimate the water consumed by AI model inference through data center cooling and upstream electricity generation.

## Background

AI inference consumes water in two ways:
1. **On-site cooling** (WUE site) — water evaporated in data center cooling towers
2. **Upstream electricity** (WUE source) — water used to generate the electricity that powers the hardware

Research (Li et al., "Making AI Less Thirsty") estimates ~16.9 mL per medium response at U.S. averages.

**Formula:**
```
water_mL = (tokens / 1M) * energy_wh_per_mtok / 1000 * (wue_site / pue + wue_source) * 1000
```

## Classes

### `WaterCalculator`

Estimates water usage in milliliters. Source: `src/tokenmeter/water/calculator.py`

```python
from tokenmeter.water.calculator import WaterCalculator

calc = WaterCalculator()
```

**Constructor:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `registry` | `WaterRegistry \| None` | `None` | Custom energy data registry |
| `profile` | `WaterProfile \| None` | `None` | Environmental factors (defaults to U.S. averages) |

**Methods:**

#### `calculate(model, input_tokens, output_tokens, cache_read_tokens=0, cache_write_tokens=0) -> Decimal`

Returns estimated water usage in mL. Returns `Decimal("0")` if model is unknown.

All token types contribute equally to energy (unlike cost, where input/output have different prices).

```python
water = calc.calculate(model="claude-sonnet-4-5", input_tokens=1000, output_tokens=500)
# Decimal('1.35')
```

#### `estimate_input_water(text, model) -> Decimal`

Heuristic-based estimate (~4 chars per token):

```python
water = calc.estimate_input_water("Hello, world!", model="claude-sonnet-4-5")
```

### `WaterRegistry`

Model energy data registry. Source: `src/tokenmeter/water/__init__.py`

```python
from tokenmeter.water import WaterRegistry

registry = WaterRegistry()
```

**Methods:**

#### `get(model) -> ModelWaterProfile | None`

Look up energy profile. Returns `None` (not an error) for unknown models — water estimation is best-effort.

```python
profile = registry.get("claude-sonnet-4-5")
if profile:
    print(profile.energy_per_mtok)  # Decimal('450')
```

#### `register(profile: ModelWaterProfile) -> None`

Register custom model energy data:

```python
from tokenmeter._types import ModelWaterProfile
from decimal import Decimal

registry.register(ModelWaterProfile(
    model_id="my-model",
    provider="custom",
    energy_per_mtok=Decimal("200"),
))
```

#### `list_models(provider=None) -> list[str]`

List all models with energy data.

### `WaterProfile`

Environmental factors for water estimation. Source: `src/tokenmeter/_types.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pue` | `Decimal` | `1.2` | Power Usage Effectiveness |
| `wue_site` | `Decimal` | `1.8` | On-site cooling (L/kWh) |
| `wue_source` | `Decimal` | `0.5` | Upstream electricity (L/kWh) |

Defaults are U.S. averages. Create a custom profile for different regions:

```python
from tokenmeter._types import WaterProfile
from decimal import Decimal

# European data center (more efficient cooling, cleaner grid)
eu_profile = WaterProfile(
    pue=Decimal("1.1"),
    wue_site=Decimal("1.0"),
    wue_source=Decimal("0.3"),
)
meter = tokenmeter.Meter(water_profile=eu_profile)
```

### `ModelWaterProfile`

Energy characteristics for a model. Source: `src/tokenmeter/_types.py`

| Field | Type | Description |
|-------|------|-------------|
| `model_id` | `str` | Model identifier |
| `provider` | `str` | Provider name |
| `energy_per_mtok` | `Decimal` | Wh per million tokens |

## Built-in Energy Data

Source: `src/tokenmeter/water/_data.py`

| Model | energy_per_mtok (Wh) |
|-------|---------------------|
| claude-opus-4-6/4-5/4-1/4 | 900 |
| claude-sonnet-4-5/4 | 450 |
| claude-haiku-4-5 | 100 |
| claude-haiku-3-5 | 80 |
| claude-haiku-3 | 50 |
| gpt-5.1/5 | 500 |
| gpt-5-mini | 100 |
| gpt-5-nano, gpt-4.1-nano | 30 |
| gpt-4.1 | 300 |
| gpt-4.1-mini | 80 |
| gpt-4o | 300 |
| gpt-4o-mini | 50 |
| o1 | 800 |
| o3 | 500 |
| o3-mini, o4-mini | 200 |

## Usage via the Meter Facade

```python
import tokenmeter

meter = tokenmeter.Meter()

# Estimate water for a prompt
water = meter.estimate_water("Explain quantum computing", model="claude-sonnet-4-5")
print(f"Estimated water: ~{water:.1f} mL")

# Record usage — water_ml is computed automatically
record = meter.record(api_response)
print(f"Water used: ~{record.water_ml:.1f} mL")

# Query total water
total = meter.total_water()
total_by_model = meter.total_water(model="claude-sonnet-4-5")
```

## Notes

- Energy values are rough estimates derived from published benchmarks. Actual energy depends on hardware, batch size, and data center configuration.
- Water estimation is best-effort: unknown models return `Decimal("0")`.
- The `water_ml` field is persisted in SQLite and JSON Lines storage backends.
- Model name aliases are shared with the pricing registry (e.g., `"claude-sonnet-4-5-20250929"` resolves correctly).
