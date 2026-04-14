#!/usr/bin/env python3
"""
NEXUS Framework - Input/Output Sanitization

Security layer for input validation and output sanitization.
Uses bleach for HTML/XSS protection and custom validation.
"""

from __future__ import annotations

import re
import html
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False
    bleach = None


@dataclass
class SanitizationConfig:
    """Configuration for sanitization behavior."""
    allowed_tags: List[str] = field(default_factory=lambda: [])
    allowed_attributes: Dict[str, List[str]] = field(default_factory=dict)
    strip_comments: bool = True
    max_length: int = 100000
    escape_html: bool = True
    allow_markdown: bool = False


class Sanitizer:
    """
    Input/Output sanitization with XSS protection.
    Thread-safe with configurable behavior.
    """

    def __init__(self, config: Optional[SanitizationConfig] = None):
        self._config = config or SanitizationConfig()

    def sanitize_input(self, text: str) -> str:
        """Sanitize user input for safe processing."""
        if not isinstance(text, str):
            return str(text)
        text = self._strip_control_chars(text)
        if self._config.escape_html:
            text = self._escape_html(text)
        text = self._limit_length(text)
        return text

    def sanitize_output(self, text: str, context: str = "html") -> str:
        """Sanitize output for safe display."""
        if not isinstance(text, str):
            return str(text)
        if context == "html" or context == "web":
            return self._sanitize_html(text)
        elif context == "json":
            return self._sanitize_json_string(text)
        elif context == "markdown":
            return self._sanitize_markdown(text)
        return text

    def _strip_control_chars(self, text: str) -> str:
        """Remove dangerous control characters."""
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
        return text

    def _escape_html(self, text: str) -> str:
        """Escape HTML entities."""
        if BLEACH_AVAILABLE and self._config.allowed_tags:
            return bleach.clean(
                text,
                tags=self._config.allowed_tags,
                attributes=self._config.allowed_attributes,
                strip=self._config.strip_comments
            )
        return html.escape(text, quote=True)

    def _sanitize_html(self, text: str) -> str:
        """Sanitize HTML content."""
        if BLEACH_AVAILABLE:
            return bleach.clean(
                text,
                tags=self._config.allowed_tags,
                attributes=self._config.allowed_attributes,
                strip=self._config.strip_comments
            )
        return html.escape(text, quote=True)

    def _sanitize_json_string(self, text: str) -> str:
        """Sanitize for JSON string context."""
        text = text.replace(chr(92), chr(92) + chr(92))
        text = text.replace(chr(34), chr(92) + chr(34))
        text = text.replace(chr(10), chr(92) + chr(110))
        text = text.replace(chr(13), chr(92) + chr(114))
        text = text.replace(chr(9), chr(92) + chr(116))
        return text

    def _sanitize_markdown(self, text: str) -> str:
        """Sanitize markdown content."""
        if not self._config.allow_markdown:
            text = re.sub(r"([*_`~#\[\]\(\)])", r"\\", text)
        return text

    def _limit_length(self, text: str) -> str:
        """Limit text length."""
        if len(text) > self._config.max_length:
            return text[:self._config.max_length] + "...[truncated]"
        return text

    def sanitize_dict(self, data: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
        """Sanitize all string values in a dictionary."""
        result = {}
        for key, value in data.items():
            safe_key = self.sanitize_input(str(key))
            if isinstance(value, str):
                result[safe_key] = self.sanitize_input(value)
            elif isinstance(value, dict) and deep:
                result[safe_key] = self.sanitize_dict(value, deep)
            elif isinstance(value, list) and deep:
                result[safe_key] = self.sanitize_list(value, deep)
            else:
                result[safe_key] = value
        return result

    def sanitize_list(self, data: List[Any], deep: bool = True) -> List[Any]:
        """Sanitize all string values in a list."""
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.sanitize_input(item))
            elif isinstance(item, dict) and deep:
                result.append(self.sanitize_dict(item, deep))
            elif isinstance(item, list) and deep:
                result.append(self.sanitize_list(item, deep))
            else:
                result.append(item)
        return result


# Convenience functions
def sanitize_input(text: str) -> str:
    """Quick input sanitization."""
    return Sanitizer().sanitize_input(text)


def sanitize_output(text: str, context: str = "html") -> str:
    """Quick output sanitization."""
    return Sanitizer().sanitize_output(text, context)


def sanitize_html(text: str) -> str:
    """Quick HTML sanitization."""
    return Sanitizer().sanitize_output(text, "html")


__all__ = ["Sanitizer", "SanitizationConfig", "sanitize_input", "sanitize_output", "sanitize_html"]