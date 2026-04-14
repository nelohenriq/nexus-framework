# NEXUS Framework - Unit Tests for Security

import pytest
import sys
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.security.sanitizer import Sanitizer


class TestSanitizer:
    def test_sanitize_html():
        s = Sanitizer()
        result = s.sanitize_input("<script>alert(1)</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result or result == "Hello"

    def test_sanitize_plain_text():
        s = Sanitizer()
        result = s.sanitize_input("Hello World")
        assert result == "Hello World"

    def test_output_sanitization():
        s = Sanitizer()
        result = s.sanitize_output("Normal output")
        assert result == "Normal output"

    def test_xss_protection():
        s = Sanitizer()
        malicious = "<img src=x onerror=alert(1)>"
        result = s.sanitize_input(malicious)
        assert "onerror" not in result