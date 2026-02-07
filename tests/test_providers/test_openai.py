from tests.conftest import make_openai_response
from tokenmeter.providers.openai import OpenAIProvider


class TestOpenAIProvider:
    def test_name(self):
        provider = OpenAIProvider()
        assert provider.name == "openai"

    def test_count_tokens_local(self):
        provider = OpenAIProvider()
        tokens = provider.count_tokens_local("Hello world, this is a test.", "gpt-4o")
        assert tokens > 0

    def test_extract_usage(self):
        provider = OpenAIProvider()
        resp = make_openai_response(prompt_tokens=200, completion_tokens=100)
        usage = provider.extract_usage(resp)
        assert usage["input_tokens"] == 200
        assert usage["output_tokens"] == 100

    def test_extract_usage_with_cache(self):
        provider = OpenAIProvider()
        resp = make_openai_response(prompt_tokens=200, completion_tokens=100, cached_tokens=50)
        usage = provider.extract_usage(resp)
        assert usage["cache_read_tokens"] == 50

    def test_extract_model(self):
        provider = OpenAIProvider()
        resp = make_openai_response(model="gpt-4.1")
        assert provider.extract_model(resp) == "gpt-4.1"

    def test_matches_response(self):
        provider = OpenAIProvider()
        resp = make_openai_response()
        assert provider.matches_response(resp) is True

    def test_does_not_match_anthropic(self):
        from tests.conftest import make_anthropic_response
        provider = OpenAIProvider()
        resp = make_anthropic_response()
        assert provider.matches_response(resp) is False
