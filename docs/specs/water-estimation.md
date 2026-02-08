# Spec: Water Estimation

## Motivation

AI model inference consumes significant water through data center cooling (on-site) and electricity generation (upstream). Research (Li et al., "Making AI Less Thirsty") estimates ~16.9 mL per medium response at U.S. averages. tokenmeter already tracks cost per-token; water estimation follows the same pattern using energy-per-token data and configurable environmental factors.

## Formula

```
water_mL = (tokens / 1M) * energy_wh_per_mtok / 1000 * (wue_site / pue + wue_source) * 1000
```

Default environmental factors (U.S. averages):
- PUE (Power Usage Effectiveness): 1.2
- WUE site (on-site cooling): 1.8 L/kWh
- WUE source (upstream electricity): 0.5 L/kWh

## API Design

### `WaterCalculator`

- `calculate(model, input_tokens, output_tokens, cache_read_tokens=0, cache_write_tokens=0) -> Decimal` — returns mL; returns `Decimal("0")` if model unknown
- `estimate_input_water(text, model) -> Decimal` — heuristic (~4 chars/token) pre-call estimate

### `WaterRegistry`

- `get(model) -> ModelWaterProfile | None` — returns `None` (not error) for unknown models
- `register(profile: ModelWaterProfile)` — custom model energy data
- `list_models(provider=None) -> list[str]`

### Types

**WaterProfile** (frozen): `pue`, `wue_site`, `wue_source` — all `Decimal` with U.S. defaults.

**ModelWaterProfile** (frozen): `model_id`, `provider`, `energy_per_mtok` (Wh per million tokens).

### Meter Facade

- `Meter(water_profile=WaterProfile())` — accepts custom environmental factors
- `meter.water` — the `WaterCalculator` instance
- `meter.estimate_water(text, model) -> Decimal`
- `meter.total_water(**filters) -> Decimal`

## Data Model

- All token types (input, output, cache_read, cache_write) contribute equally to energy.
- `water_ml` field added to `UsageRecord` (default `Decimal("0")`).
- Persisted in SQLite (`water_ml TEXT DEFAULT '0'`) and JSON Lines (`"water_ml": "0"`).
- SQLite migration adds column to existing databases.

## Built-in Energy Data (Wh per million tokens)

| Model | energy_per_mtok |
|-------|----------------|
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

## Edge Cases

- Unknown model -> `Decimal("0")` (best-effort, no error)
- Zero tokens -> `Decimal("0")`
- Custom `WaterProfile` with different PUE/WUE for non-U.S. data centers
- Aliases shared with pricing registry (dated model IDs resolve correctly)

## Files

- `src/tokenmeter/water/__init__.py`
- `src/tokenmeter/water/_data.py`
- `src/tokenmeter/water/calculator.py`
- `src/tokenmeter/_types.py` (WaterProfile, ModelWaterProfile, UsageRecord.water_ml)
