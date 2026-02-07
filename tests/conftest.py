from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import pytest

import tokenmeter


@pytest.fixture
def meter():
    return tokenmeter.Meter(storage="memory")


@pytest.fixture
def meter_with_budget(meter):
    meter.set_budget(limit=1.00, period="total", action="block")
    return meter


# --- Mock response objects ---
# We need real classes (not SimpleNamespace) so that __module__ is inspectable
# by the provider auto-detection logic.


class _AnthropicUsage:
    __module__ = "anthropic.types"

    def __init__(self, input_tokens, output_tokens, cache_read_input_tokens=0, cache_creation_input_tokens=0):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.cache_read_input_tokens = cache_read_input_tokens
        self.cache_creation_input_tokens = cache_creation_input_tokens


class _AnthropicMessage:
    __module__ = "anthropic.types"

    def __init__(self, model, usage):
        self.model = model
        self.usage = usage


class _OpenAITokenDetails:
    __module__ = "openai.types.chat"

    def __init__(self, cached_tokens):
        self.cached_tokens = cached_tokens


class _OpenAIUsage:
    __module__ = "openai.types.chat"

    def __init__(self, prompt_tokens, completion_tokens, prompt_tokens_details=None):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.prompt_tokens_details = prompt_tokens_details


class _OpenAIChatCompletion:
    __module__ = "openai.types.chat"

    def __init__(self, model, usage):
        self.model = model
        self.usage = usage


def make_anthropic_response(
    model: str = "claude-sonnet-4-5",
    input_tokens: int = 100,
    output_tokens: int = 50,
    cache_read_input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
):
    """Create a mock Anthropic-style response object."""
    usage = _AnthropicUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_read_input_tokens=cache_read_input_tokens,
        cache_creation_input_tokens=cache_creation_input_tokens,
    )
    return _AnthropicMessage(model=model, usage=usage)


def make_openai_response(
    model: str = "gpt-4o",
    prompt_tokens: int = 100,
    completion_tokens: int = 50,
    cached_tokens: int = 0,
):
    """Create a mock OpenAI-style response object."""
    details = _OpenAITokenDetails(cached_tokens=cached_tokens) if cached_tokens else None
    usage = _OpenAIUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        prompt_tokens_details=details,
    )
    return _OpenAIChatCompletion(model=model, usage=usage)
