# References: Providers

Sources consulted during design and implementation of the provider system.

## Provider SDK Documentation

- **Anthropic Python SDK**
  https://docs.anthropic.com/en/api/client-sdks
  https://github.com/anthropics/anthropic-sdk-python
  Used for: understanding response object structure (`anthropic.types.Message`), usage fields (`input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`), and `__module__` attribute for auto-detection.

- **OpenAI Python SDK**
  https://platform.openai.com/docs/api-reference
  https://github.com/openai/openai-python
  Used for: understanding response object structure (`openai.types.chat.ChatCompletion`), usage fields (`prompt_tokens`, `completion_tokens`, `prompt_tokens_details.cached_tokens`), and `__module__` attribute for auto-detection.

## Tokenizer References

- **tiktoken (OpenAI tokenizer)**
  https://github.com/openai/tiktoken
  Used for: accurate local token counting for OpenAI models. Optional dependency — falls back to heuristic when not installed.

- **Anthropic token counting documentation**
  https://docs.anthropic.com/en/docs/build-with-claude/token-counting
  Used for: understanding Anthropic's token counting approach. The SDK's `count_tokens` method requires an API call; local counting falls back to heuristic.

## Design Patterns

- **Strategy Pattern**
  General software architecture pattern. Used for: the `Provider` ABC that defines a common interface, with `AnthropicProvider` and `OpenAIProvider` as concrete strategies.

- **Service Locator / Registry Pattern**
  General software architecture pattern. Used for: `ProviderRegistry` that holds registered providers and auto-detects the correct one from a response object.

## Design Decisions

| Decision | Source |
|----------|--------|
| Auto-detect via `__module__` inspection | Anthropic/OpenAI SDK response classes set `__module__` to their package paths |
| ~4 chars per token heuristic fallback | Common industry approximation for English text tokenization |
| ~4 tokens overhead per chat message | OpenAI tokenizer docs note ~4 tokens for role/delimiters per message |
| 3 priming tokens added to message counts | OpenAI chat format documentation |
| Optional tokenizer dependencies | Core library should work without heavy SDK installs |
| Provider inferred from model name prefixes | Convention: `"claude"` = Anthropic, `"gpt"/"o1"/"o3"/"o4"` = OpenAI |
