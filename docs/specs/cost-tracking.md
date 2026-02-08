# Spec: Cost Tracking

## Motivation

AI API calls are billed per token, with different rates for input, output, cache read, cache write, and batch operations. Developers need a way to calculate costs accurately using `Decimal` arithmetic (not floating point) and to stay current with provider pricing without hardcoding rates throughout their applications.

## API Design

### `CostCalculator` (stateless)

- `calculate(model, input_tokens, output_tokens, cache_read_tokens=0, cache_write_tokens=0) -> Decimal` — total cost in USD
- `calculate_detailed(model, input_tokens, output_tokens, ...) -> dict[str, Decimal]` — itemized breakdown (input_cost, output_cost, cache_read_cost, cache_write_cost, total_cost)
- `estimate_input_cost(text, model) -> Decimal` — heuristic (~4 chars/token) pre-call estimate

### `PricingRegistry`

- `get(model) -> ModelPricing` — raises `UnknownModelError` if not found
- `register(pricing: ModelPricing)` — add/override model pricing
- `add_alias(alias, model_id)` — map alternate names to canonical IDs
- `list_models(provider=None) -> list[str]`

### `ModelPricing` (frozen dataclass)

Fields: `model_id`, `provider`, `input_per_mtok`, `output_per_mtok`, `cache_read_per_mtok`, `cache_write_per_mtok`, `batch_input_per_mtok`, `batch_output_per_mtok`.

## Data Model

- All monetary values are `Decimal` (stored as TEXT in SQLite, string in JSON).
- Cost formula: `(tokens / 1,000,000) * price_per_mtok` for each token type.
- Cache token prices are optional (`None` treated as zero cost).

## Built-in Data

Pricing tables in `pricing/_data.py` cover:
- **Anthropic:** Claude Opus 4.6/4.5/4.1/4, Sonnet 4.5/4, Haiku 4.5/3.5/3
- **OpenAI:** GPT-5.1, 5, 5-mini, 5-nano, 4.1, 4.1-mini, 4.1-nano, 4o, 4o-mini, o3, o3-mini, o4-mini, o1

Aliases resolve dated model IDs (e.g., `claude-sonnet-4-5-20250929`) to canonical names.

## Edge Cases

- Unknown model -> `UnknownModelError` (not silent zero)
- Zero tokens -> `Decimal("0")` cost
- `None` cache pricing -> zero cost for that token type
- Model names are case-insensitive and trimmed

## Files

- `src/tokenmeter/cost.py`
- `src/tokenmeter/pricing/__init__.py`
- `src/tokenmeter/pricing/_data.py`
- `src/tokenmeter/_types.py` (ModelPricing, UnknownModelError)
