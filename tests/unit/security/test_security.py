# NEXUS Framework - Unit Tests for Security Layer

import pytest
import sys
sys.path.insert(0, "/a0/usr/projects/meta_agentic_framework")

from nexus.security.sanitizer import Sanitizer

class TestSanitizer:
    def test_sanitize_html(self):
        s = Sanitizer()
        result = s.sanitize_input("<p>Hello</p>")
        assert "<" not in result

    def test_sanitize_plain_text(self):
        s = Sanitizer()
        result = s.sanitize_input("Hello world")
        assert result == "Hello world"

    def test_output_sanitization(self):
        s = Sanitizer()
        result = s.sanitize_output("Some output")
        assert result == "Some output"

    def test_xss_protection(self):
        s = Sanitizer()
        malicious = "<img src=x onerror=alert(1)>"
        result = s.sanitize_input(malicious)
        assert "<" not in result
        assert ">" not in result