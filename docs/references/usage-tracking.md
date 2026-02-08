# References: Usage Tracking

Sources consulted during design and implementation of the usage tracking feature.

## Provider API Documentation

- **Anthropic Messages API — Usage object**
  https://docs.anthropic.com/en/api/messages
  Used for: understanding the response structure (`response.usage.input_tokens`, `response.usage.output_tokens`, cache fields). Informed `extract_usage()` in the Anthropic provider.

- **OpenAI Chat Completions API — Usage object**
  https://platform.openai.com/docs/api-reference/chat/object
  Used for: understanding the response structure (`response.usage.prompt_tokens`, `response.usage.completion_tokens`, `prompt_tokens_details.cached_tokens`). Informed `extract_usage()` in the OpenAI provider.

## Design Patterns

- **Repository Pattern**
  General software architecture pattern. Used for: the `StorageBackend` abstraction that separates record persistence from query logic, allowing the tracker to work with any backend.

- **Facade Pattern**
  General software architecture pattern. Used for: the `Meter` class that wires `UsageTracker`, `CostCalculator`, `BudgetManager`, and `AlertManager` together behind a simplified API.

## Language References

- **Python `uuid` module documentation**
  https://docs.python.org/3/library/uuid.html
  Used for: generating unique record IDs (`uuid.uuid4()`).

- **Python `datetime` module documentation**
  https://docs.python.org/3/library/datetime.html
  Used for: timestamps on records, time-range filtering in queries.

## Design Decisions

| Decision | Source |
|----------|--------|
| Auto-detect provider from response `__module__` | Anthropic/OpenAI SDK response class structures |
| Infer provider from model name prefix | Convention: `"claude"` = Anthropic, `"gpt"/"o1"/"o3"/"o4"` = OpenAI |
| Arbitrary string tags for filtering | Common observability pattern (key=value dimensions) |
| Session ID auto-generated per tracker instance | Provides automatic session grouping without user configuration |
