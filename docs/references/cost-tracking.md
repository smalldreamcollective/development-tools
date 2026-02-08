# References: Cost Tracking

Sources consulted during design and implementation of the cost tracking feature.

## Provider Pricing Documentation

- **Anthropic Pricing**
  https://docs.anthropic.com/en/docs/about-claude/pricing
  Used for: all Claude model per-million-token rates (input, output, cache read, cache write, batch). Source of the pricing tables in `pricing/_data.py`.

- **OpenAI API Pricing**
  https://openai.com/api/pricing/
  Used for: all GPT and o-series model per-million-token rates. Source of the pricing tables in `pricing/_data.py`.

## Language & Library References

- **Python `decimal` module documentation**
  https://docs.python.org/3/library/decimal.html
  Used for: choosing `Decimal` over `float` for monetary arithmetic to avoid floating-point precision errors. Informed the convention of storing costs as `Decimal` throughout and as TEXT/string in storage backends.

- **Python `dataclasses` module documentation**
  https://docs.python.org/3/library/dataclasses.html
  Used for: `@dataclass(frozen=True)` pattern for immutable configuration types like `ModelPricing`.

## Design Decisions

| Decision | Source |
|----------|--------|
| Per-million-token pricing unit | Anthropic and OpenAI both quote prices per MTok |
| `Decimal` for all monetary values | Python decimal module best practices |
| Alias resolution for dated model IDs | Anthropic/OpenAI version their model IDs with dates |
| Separate input/output/cache pricing | Both providers charge different rates per token type |
| `UnknownModelError` for missing models | Fail-loud approach — cost must be accurate, not silently zero |
