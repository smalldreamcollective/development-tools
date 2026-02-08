# Spec: Usage Tracking

## Motivation

Applications need to record every API call's token usage and cost, then query and aggregate that data by model, provider, user, session, time range, or custom tags. This provides visibility into spending patterns and feeds into budgets and alerts.

## API Design

### `UsageTracker`

- `record(response, user_id=None, session_id=None, **tags) -> UsageRecord` — auto-detect provider from response object, extract tokens, compute cost and water, persist
- `record_manual(model, input_tokens, output_tokens, ..., **tags) -> UsageRecord` — record from known token counts (infers provider from model name)
- `get_total(**filters) -> Decimal` — sum total_cost across matching records
- `get_total_water(**filters) -> Decimal` — sum water_ml across matching records
- `get_records(**filters) -> list[UsageRecord]` — return individual records
- `get_summary(group_by="model") -> dict[str, Decimal]` — aggregate spending

### Filter Parameters (shared across get_total, get_total_water, get_records)

- `provider`, `model`, `user_id`, `session_id` — exact match
- `since`, `until` — datetime range
- `tags` — dict of key=value pairs (all must match)

### `UsageRecord` (dataclass)

Fields: `id` (UUID), `timestamp`, `provider`, `model`, `input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens`, `input_cost`, `output_cost`, `total_cost`, `session_id`, `user_id`, `tags`, `is_estimate`, `water_ml`.

## Data Model

- Each record is a complete snapshot of one API call.
- Session ID auto-generated per `UsageTracker` instance if not provided.
- Provider inferred from model name: `"claude"` -> anthropic, `"gpt"/"o1"/"o3"/"o4"` -> openai.
- Tags are arbitrary string key-value pairs for user-defined dimensions.

## Edge Cases

- Unknown provider from model name -> `"unknown"` in `record_manual`
- Auto-detect failure in `record()` -> raises `ValueError` from ProviderRegistry
- Empty tags dict -> matches all records (no tag filter applied)

## Files

- `src/tokenmeter/tracker.py`
- `src/tokenmeter/_types.py` (UsageRecord)
