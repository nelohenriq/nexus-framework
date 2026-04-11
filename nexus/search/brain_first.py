"""Brain-First Lookup Protocol Implementation."""

from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class LookupResult:
    source: str
    found: bool
    data: Any = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrainFirstLookup:
    """Check internal knowledge (brain) before external APIs."""

    def __init__(self, internal_store: Optional[Dict[str, Any]] = None):
        self.internal_store = internal_store or {}
        self.external_apis: Dict[str, Callable] = {}
        self.cache: Dict[str, LookupResult] = {}

    def register_external_api(self, name: str, fetch_func: Callable):
        self.external_apis[name] = fetch_func

    def lookup(self, query: str, use_external: bool = True) -> LookupResult:
        cache_key = query.lower().strip()
        if cache_key in self.cache:
            return self.cache[cache_key]
        internal_result = self._search_internal(query)
        if internal_result.found:
            self.cache[cache_key] = internal_result
            return internal_result
        if use_external:
            external_result = self._search_external(query)
            if external_result.found:
                self.cache[cache_key] = external_result
                return external_result
        return LookupResult(source="none", found=False)

    def _search_internal(self, query: str) -> LookupResult:
        query_lower = query.lower()
        for key, value in self.internal_store.items():
            if query_lower in key.lower():
                return LookupResult(source="internal", found=True, data=value, confidence=1.0)
        return LookupResult(source="internal", found=False)

    def _search_external(self, query: str) -> LookupResult:
        for api_name, fetch_func in self.external_apis.items():
            try:
                result = fetch_func(query)
                if result:
                    return LookupResult(source=api_name, found=True, data=result, confidence=0.8)
            except Exception:
                continue
        return LookupResult(source="external", found=False)

    def add_to_brain(self, key: str, value: Any):
        self.internal_store[key] = value


def create_brain_first(internal_store: Optional[Dict] = None) -> BrainFirstLookup:
    return BrainFirstLookup(internal_store=internal_store)