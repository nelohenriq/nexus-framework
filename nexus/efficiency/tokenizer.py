"""
NEXUS Framework - Precise Token Counting

Uses tiktoken for accurate token counting across models.
Replaces inaccurate .split() based estimation.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Optional
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    tiktoken = None


@dataclass
class TokenCount:
    """Token count result with metadata."""
    tokens: int
    model: str
    encoding_name: str
    accurate: bool = True


class Tokenizer:
    """
    Precise token counting using tiktoken.
    Thread-safe with encoding caching.
    """

    # Model to encoding mapping
    MODEL_ENCODINGS = {
        "gpt-4": "cl100k_base",
        "gpt-4-turbo": "cl100k_base",
        "gpt-3.5-turbo": "cl100k_base",
        "gpt-3.5": "cl100k_base",
        "gpt-4o": "o200k_base",
        "gpt-4o-mini": "o200k_base",
        "claude-3": "cl100k_base",
        "claude-2": "cl100k_base",
        "text-embedding-ada-002": "cl100k_base",
        "llama": "cl100k_base",
        "mistral": "cl100k_base",
        "default": "cl100k_base",
    }

    def __init__(self, model: str = "default"):
        self._model = model
        self._lock = threading.Lock()
        self._encodings: dict = {}
        self._fallback_ratio = 4

    def _get_encoding(self, model: str) -> Optional[object]:
        """Get or create encoding for model (thread-safe)."""
        if not TIKTOKEN_AVAILABLE:
            return None
        encoding_name = self.MODEL_ENCODINGS.get(model, self.MODEL_ENCODINGS["default"])
        with self._lock:
            if encoding_name not in self._encodings:
                try:
                    self._encodings[encoding_name] = tiktoken.get_encoding(encoding_name)
                except Exception:
                    return None
            return self._encodings[encoding_name]
        return self._encodings[encoding_name]

    def count(self, text: str, model: Optional[str] = None) -> TokenCount:
        """Count tokens in text for specified model."""
        model = model or self._model
        encoding = self._get_encoding(model)
        if encoding:
            try:
                tokens = len(encoding.encode(text))
                return TokenCount(
                    tokens=tokens,
                    model=model,
                    encoding_name=self.MODEL_ENCODINGS.get(model, "cl100k_base"),
                    accurate=True
                )
            except Exception:
                pass
        # Fallback: character-based estimation
        estimated = len(text) // self._fallback_ratio
        return TokenCount(
            tokens=estimated,
            model=model,
            encoding_name="fallback",
            accurate=False
        )

    def count_messages(self, messages: list[dict], model: Optional[str] = None) -> TokenCount:
        """Count tokens in a list of chat messages."""
        total = 0
        model = model or self._model
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += self.count(content, model).tokens
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        total += self.count(part["text"], model).tokens
        # Add message overhead (~4 tokens per message)
        total += len(messages) * 4
        return TokenCount(
            tokens=total,
            model=model,
            encoding_name=self.MODEL_ENCODINGS.get(model, "cl100k_base"),
            accurate=TIKTOKEN_AVAILABLE
        )

    def truncate(self, text: str, max_tokens: int, model: Optional[str] = None) -> str:
        """Truncate text to fit within max_tokens."""
        model = model or self._model
        encoding = self._get_encoding(model)
        if not encoding:
            # Fallback: character-based truncation
            return text[:max_tokens * self._fallback_ratio]
        try:
            tokens = encoding.encode(text)
            if len(tokens) <= max_tokens:
                return text
            truncated = tokens[:max_tokens]
            return encoding.decode(truncated)
        except Exception:
            return text[:max_tokens * self._fallback_ratio]


# Convenience functions
def count_tokens(text: str, model: str = "default") -> int:
    """Quick token count for text."""
    tokenizer = Tokenizer(model)
    return tokenizer.count(text).tokens


def count_message_tokens(messages: list[dict], model: str = "default") -> int:
    """Quick token count for messages."""
    tokenizer = Tokenizer(model)
    return tokenizer.count_messages(messages).tokens


__all__ = ["Tokenizer", "TokenCount", "count_tokens", "count_message_tokens"]