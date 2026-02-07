from tests.conftest import make_anthropic_response
from tokenmeter.providers.anthropic import AnthropicProvider


class TestAnthropicProvider:
    def test_name(self):
        provider = AnthropicProvider()
        assert provider.name == "anthropic"

    def test_count_tokens_local(self):
        provider = AnthropicProvider()
        tokens = provider.count_tokens_local("Hello world, this is a test.", "claude-sonnet-4-5")
        assert tokens > 0

    def test_extract_usage(self):
        provider = AnthropicProvider()
        resp = make_anthropic_response(input_tokens=150, output_tokens=75)
        usage = provider.extract_usage(resp)
        assert usage["input_tokens"] == 150
        assert usage["output_tokens"] == 75

    def test_extract_usage_with_cache(self):
        provider = AnthropicProvider()
        resp = make_anthropic_response(
            input_tokens=150,
            output_tokens=75,
            cache_read_input_tokens=50,
            cache_creation_input_tokens=30,
        )
        usage = provider.extract_usage(resp)
        assert usage["cache_read_tokens"] == 50
        assert usage["cache_write_tokens"] == 30

    def test_extract_model(self):
        provider = AnthropicProvider()
        resp = make_anthropic_response(model="claude-opus-4-5")
        assert provider.extract_model(resp) == "claude-opus-4-5"

    def test_matches_response(self):
        provider = AnthropicProvider()
        resp = make_anthropic_response()
        assert provider.matches_response(resp) is True

    def test_does_not_match_openai(self):
        from tests.conftest import make_openai_response
        provider = AnthropicProvider()
        resp = make_openai_response()
        assert provider.matches_response(resp) is False
