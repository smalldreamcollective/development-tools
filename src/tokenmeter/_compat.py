"""Graceful handling of optional dependencies."""

from __future__ import annotations

from typing import Any


def get_tiktoken() -> Any | None:
    try:
        import tiktoken
        return tiktoken
    except ImportError:
        return None


def get_anthropic() -> Any | None:
    try:
        import anthropic
        return anthropic
    except ImportError:
        return None
