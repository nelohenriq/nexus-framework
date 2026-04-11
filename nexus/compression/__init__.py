#!/usr/bin/env python3
"""
NEXUS Framework - TOON Compression

Token-Oriented Object Notation (TOON) for efficient data representation.
Achieves ~40% token reduction compared to JSON.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class TOONConfig:
    """Configuration for TOON serialization."""
    indent: str = " " * 2
    array_format: str = "table"
    include_types: bool = False
    max_line_length: int = 120


class TOONCompression:
    """TOON format encoder/decoder for efficient data representation."""

    def __init__(self, config: Optional[TOONConfig] = None):
        self._config = config or TOONConfig()

    def encode(self, data: Dict[str, Any]) -> str:
        """Encode a dictionary to TOON format."""
        return self._encode_dict(data, 0)

    def _encode_dict(self, data: Dict[str, Any], level: int) -> str:
        """Encode a dictionary."""
        indent = self._config.indent * level
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(indent + key + ":")
                lines.append(self._encode_dict(value, level + 1))
            elif isinstance(value, list) and value and all(isinstance(i, dict) for i in value):
                lines.append(self._encode_table_array(key, value, level))
            elif isinstance(value, list):
                lines.append(self._encode_list(key, value, level))
            elif isinstance(value, (int, float, bool)) or value is None:
                lines.append(indent + key + ": " + str(value))
            else:
                str_val = str(value).replace(chr(10), "\\n")
                if "," in str_val or str_val.startswith(" ") or str_val.endswith(" "):
                    dq = chr(34)
                    lines.append(indent + key + ": " + dq + str_val + dq)
                else:
                    lines.append(indent + key + ": " + str_val)
        return chr(10).join(lines)

    def _encode_table_array(self, key: str, items: List[Dict], level: int) -> str:
        """Encode an array of objects in tabular format."""
        indent = self._config.indent * level
        if not items:
            return indent + key + "[0]:"
        all_keys = []
        for item in items:
            for k in item.keys():
                if k not in all_keys:
                    all_keys.append(k)
        header = ",".join(all_keys)
        lines = [indent + key + "[" + str(len(items)) + "]{" + header + "}:"]
        item_indent = self._config.indent * (level + 1)
        for item in items:
            values = []
            for k in all_keys:
                v = item.get(k, "")
                if isinstance(v, str) and ("," in v or v == ""):
                    dq = chr(34)
                    v = dq + v + dq
                values.append(str(v))
            lines.append(item_indent + ",".join(values))
        return chr(10).join(lines)

    def _encode_list(self, key: str, items: List, level: int) -> str:
        """Encode a simple list."""
        indent = self._config.indent * level
        if not items:
            return indent + key + "[0]:"
        lines = [indent + key + "[" + str(len(items)) + "]:"]
        item_indent = self._config.indent * (level + 1)
        for item in items:
            lines.append(item_indent + str(item))
        return chr(10).join(lines)

    def decode(self, toon_str: str) -> Dict[str, Any]:
        """Decode TOON format to dictionary."""
        lines = toon_str.split(chr(10))
        result, _ = self._decode_lines(lines, 0)
        return result

    def _decode_lines(self, lines: List[str], start: int) -> tuple:
        """Decode lines recursively."""
        result = {}
        i = start
        while i < len(lines):
            line = lines[i]
            if not line.strip():
                i += 1
                continue
            if ":" in line:
                colon_pos = line.index(":")
                key_part = line[:colon_pos].strip()
                value_part = line[colon_pos + 1:].strip() if colon_pos + 1 < len(line) else ""
                match = re.match(r"(.+)\\[(\\d+)\\](?:\\{([^}]+)\\})?", key_part)
                if match:
                    key = match.group(1).strip()
                    count = int(match.group(2))
                    fields = match.group(3)
                    if fields:
                        field_names = [f.strip() for f in fields.split(",")]
                        items = []
                        i += 1
                        base_indent = len(line) - len(line.lstrip())
                        while i < len(lines):
                            next_line = lines[i]
                            if not next_line.strip():
                                i += 1
                                continue
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= base_indent:
                                break
                            values = self._parse_csv_line(next_line.strip())
                            item = {}
                            for j, fname in enumerate(field_names):
                                if j < len(values):
                                    item[fname] = self._parse_value(values[j])
                            items.append(item)
                            i += 1
                        result[key] = items
                    elif count > 0 and not value_part:
                        items = []
                        i += 1
                        base_indent = len(line) - len(line.lstrip())
                        while i < len(lines):
                            next_line = lines[i]
                            if not next_line.strip():
                                i += 1
                                continue
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= base_indent:
                                break
                            items.append(self._parse_value(next_line.strip()))
                            i += 1
                        result[key] = items
                    else:
                        result[key] = []
                        i += 1
                elif value_part:
                    result[key_part] = self._parse_value(value_part)
                    i += 1
                else:
                    nested, new_i = self._decode_lines(lines, i + 1)
                    result[key_part] = nested
                    i = new_i
            else:
                i += 1
        return result, i

    def _parse_csv_line(self, line: str) -> List[str]:
        """Parse CSV line with quote handling."""
        values = []
        current = ""
        in_quotes = False
        dq = chr(34)
        for char in line:
            if char == dq:
                in_quotes = not in_quotes
            elif char == "," and in_quotes:
                current += char
            elif char == "," and not in_quotes:
                values.append(current)
                current = ""
            else:
                current += char
        values.append(current)
        return values

    def _parse_value(self, value: str) -> Any:
        """Parse a string value to appropriate type."""
        if not value:
            return ""
        if value == "None":
            return None
        if value == "True":
            return True
        if value == "False":
            return False
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                dq = chr(34)
                if value.startswith(dq) and value.endswith(dq):
                    value = value[1:-1]
                return value.replace("\\n", chr(10))

    def compress_context(self, messages: List[Dict]) -> str:
        """Compress conversation context to TOON format."""
        data = {"messages": messages}
        return self.encode(data)

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough: 1 token per 4 chars)."""
        return len(text) // 4

    def get_compression_ratio(self, data: Dict) -> float:
        """Calculate compression ratio vs JSON."""
        json_str = json.dumps(data, indent=2)
        toon_str = self.encode(data)
        return len(toon_str) / len(json_str) if json_str else 1.0


def to_toon(data: Dict[str, Any]) -> str:
    """Convert dictionary to TOON format."""
    return TOONCompression().encode(data)


def from_toon(toon_str: str) -> Dict[str, Any]:
    """Parse TOON format to dictionary."""
    return TOONCompression().decode(toon_str)


toon = TOONCompression()


__all__ = ["TOONConfig", "TOONCompression", "to_toon", "from_toon", "toon"]