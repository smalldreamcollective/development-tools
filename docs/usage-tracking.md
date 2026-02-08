# Usage Tracking

Record API usage from provider responses or manual token counts, then query and aggregate spending.

## Classes

### `UsageTracker`

Records and aggregates API usage data. Source: `src/tokenmeter/tracker.py`

```python
from tokenmeter import UsageTracker

tracker = UsageTracker()
```

**Constructor:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `storage` | `StorageBackend \| None` | `None` | Storage backend (defaults to in-memory) |
| `cost_calculator` | `CostCalculator \| None` | `None` | Cost calculator (uses built-in pricing) |
| `providers` | `ProviderRegistry \| None` | `None` | Provider registry for auto-detection |
| `session_id` | `str \| None` | `None` | Session ID (auto-generated UUID if omitted) |
| `water_calculator` | `WaterCalculator \| None` | `None` | Water calculator (no water tracking if omitted) |

**Methods:**

#### `record(response, user_id=None, session_id=None, **tags) -> UsageRecord`

Record usage from a provider API response. Auto-detects Anthropic or OpenAI.

```python
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(model="claude-sonnet-4-5", max_tokens=1024, messages=[...])

record = tracker.record(response, user_id="alice", feature="chatbot")
print(f"Cost: ${record.total_cost}, Water: {record.water_ml} mL")
```

#### `record_manual(model, input_tokens, output_tokens, ...) -> UsageRecord`

Record usage from known token counts:

```python
record = tracker.record_manual(
    model="claude-sonnet-4-5",
    input_tokens=1000,
    output_tokens=500,
    cache_read_tokens=200,
    user_id="bob",
    feature="search",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | `str` | required | Model identifier |
| `input_tokens` | `int` | required | Input token count |
| `output_tokens` | `int` | required | Output token count |
| `provider` | `str \| None` | `None` | Provider (inferred from model if omitted) |
| `cache_read_tokens` | `int` | `0` | Cache read tokens |
| `cache_write_tokens` | `int` | `0` | Cache write tokens |
| `user_id` | `str \| None` | `None` | User identifier |
| `session_id` | `str \| None` | `None` | Session (uses tracker's session if omitted) |
| `is_estimate` | `bool` | `False` | Mark as estimate vs actual usage |
| `**tags` | `str` | — | Arbitrary key=value tags |

#### `get_total(**filters) -> Decimal`

Sum of `total_cost` across matching records:

```python
tracker.get_total()                          # all spending
tracker.get_total(provider="anthropic")      # by provider
tracker.get_total(model="gpt-4o")            # by model
tracker.get_total(user_id="alice")           # by user
tracker.get_total(tags={"feature": "chat"})  # by tags
tracker.get_total(since=start, until=end)    # by time range
```

#### `get_total_water(**filters) -> Decimal`

Sum of `water_ml` across matching records. Same filter interface as `get_total()`.

#### `get_records(**filters) -> list[UsageRecord]`

Return individual records matching filters. Same filter parameters as `get_total()`.

#### `get_summary(group_by="model") -> dict[str, Decimal]`

Aggregate spending by a field:

```python
tracker.get_summary(group_by="model")      # {"claude-sonnet-4-5": Decimal("0.12"), ...}
tracker.get_summary(group_by="provider")   # {"anthropic": ..., "openai": ...}
tracker.get_summary(group_by="user_id")
tracker.get_summary(group_by="session_id")
```

### `UsageRecord`

A single API call's usage data. Source: `src/tokenmeter/_types.py`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `str` | — | Unique record ID (UUID) |
| `timestamp` | `datetime` | — | When the call was recorded |
| `provider` | `str` | — | Provider name |
| `model` | `str` | — | Model identifier |
| `input_tokens` | `int` | — | Input token count |
| `output_tokens` | `int` | — | Output token count |
| `input_cost` | `Decimal` | — | Cost of input tokens |
| `output_cost` | `Decimal` | — | Cost of output tokens |
| `total_cost` | `Decimal` | — | Total cost (input + output + cache) |
| `cache_read_tokens` | `int` | `0` | Cache read token count |
| `cache_write_tokens` | `int` | `0` | Cache write token count |
| `session_id` | `str \| None` | `None` | Session identifier |
| `user_id` | `str \| None` | `None` | User identifier |
| `tags` | `dict[str, str]` | `{}` | Arbitrary metadata tags |
| `is_estimate` | `bool` | `False` | Whether this is an estimate |
| `water_ml` | `Decimal` | `Decimal("0")` | Estimated water usage in mL |

## Examples

### Via the Meter facade (recommended)

```python
import tokenmeter

meter = tokenmeter.Meter()
record = meter.record(api_response, feature="chatbot")
print(meter.total())
print(meter.summary(group_by="model"))
```

### Standalone tracker

```python
from tokenmeter import UsageTracker, CostCalculator
from tokenmeter.water.calculator import WaterCalculator

tracker = UsageTracker(
    cost_calculator=CostCalculator(),
    water_calculator=WaterCalculator(),
)
record = tracker.record_manual("claude-sonnet-4-5", input_tokens=1000, output_tokens=500)
```
