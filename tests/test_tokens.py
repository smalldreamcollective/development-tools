import pytest

from tokenmeter.tokens import TokenCounter


@pytest.fixture
def counter():
    return TokenCounter()


class TestTokenCounter:
    def test_count_local_anthropic(self, counter):
        tokens = counter.count_local("Hello world", model="claude-sonnet-4-5")
        assert tokens > 0

    def test_count_local_openai(self, counter):
        tokens = counter.count_local("Hello world", model="gpt-4o")
        assert tokens > 0

    def test_count_local_explicit_provider(self, counter):
        tokens = counter.count_local("Hello world", model="custom-model", provider="openai")
        assert tokens > 0

    def test_count_messages_local(self, counter):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        tokens = counter.count_messages_local(messages, model="claude-sonnet-4-5")
        assert tokens > 0

    def test_infer_provider_raises_for_unknown(self, counter):
        with pytest.raises(ValueError, match="Cannot infer provider"):
            counter.count_local("Hello", model="unknown-model-xyz")

    def test_from_response(self, counter):
        from tests.conftest import make_anthropic_response
        resp = make_anthropic_response(input_tokens=150, output_tokens=75)
        usage = counter.from_response(resp)
        assert usage["input_tokens"] == 150
        assert usage["output_tokens"] == 75
