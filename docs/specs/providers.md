# Spec: Providers

## Motivation

Different AI providers (Anthropic, OpenAI) return response objects with different structures. tokenmeter needs to extract token usage and model identifiers from each, auto-detect which provider a response came from, and support adding new providers without modifying core code.

## API Design

### `Provider` (ABC)

- `name` (property) -> `str` — provider identifier
- `count_tokens_local(text, model) -> int` — local token estimate
- `extract_usage(response) -> dict[str, int]` — extract `input_tokens`, `output_tokens`, optionally `cache_read_tokens`, `cache_write_tokens`
- `extract_model(response) -> str` — extract model identifier
- `matches_response(response) -> bool` — return `True` if this provider handles the response

### `ProviderRegistry`

- `register(provider) -> None` — add custom provider
- `detect(response) -> Provider` — auto-detect from response object; raises `ValueError` if none match
- `get(name) -> Provider` — lookup by name; raises `KeyError` if not found
- `list_providers() -> list[str]`

### `TokenCounter`

- `count_local(text, model, provider=None) -> int` — count tokens using provider's tokenizer
- `count_messages_local(messages, model, provider=None) -> int` — count tokens for chat messages (adds ~4 tokens overhead per message + 3 priming tokens)
- `from_response(response) -> dict[str, int]` — extract actual usage from response

## Data Model

- Auto-detection checks `response.__module__` or `type(response).__module__`:
  - `"anthropic.types"` -> Anthropic
  - `"openai.types.chat"` -> OpenAI
- Provider inference from model name: `"claude"` -> anthropic, `"gpt"/"o1"/"o3"/"o4"` -> openai
- Token counting falls back to heuristic (~4 chars/token) when provider-specific tokenizer not installed

### Built-in Providers

**AnthropicProvider:** Extracts from `response.usage.input_tokens`, `response.usage.output_tokens`, `response.usage.cache_read_input_tokens`, `response.usage.cache_creation_input_tokens`.

**OpenAIProvider:** Extracts from `response.usage.prompt_tokens`, `response.usage.completion_tokens`, `response.usage.prompt_tokens_details.cached_tokens`.

## Edge Cases

- No matching provider for response -> `ValueError` with helpful message
- Provider not specified and can't infer from model name -> `ValueError`
- Optional tokenizer not installed -> falls back to character-based heuristic
- Cache fields missing from response -> default to 0

## Files

- `src/tokenmeter/providers/__init__.py`
- `src/tokenmeter/providers/_base.py`
- `src/tokenmeter/providers/anthropic.py`
- `src/tokenmeter/providers/openai.py`
- `src/tokenmeter/tokens.py`
