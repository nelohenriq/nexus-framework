"""
NEXUS Framework - Security Layer

16-layer security architecture inspired by OpenFang.
"""

from __future__ import annotations

import re
import time
import threading
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class SecurityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class SecurityEvent:
    layer: str
    event_type: str
    severity: SecurityLevel
    message: str
    timestamp: float = field(default_factory=time.monotonic)
    metadata: dict = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class SecurityLayer:
    def __init__(self, name: str, enabled: bool = True) -> None:
        self.name = name
        self.enabled = enabled
        self._lock = threading.Lock()
        self._events: list[SecurityEvent] = []

    def check(self, *args, **kwargs) -> tuple[bool, Optional[str]]:
        raise NotImplementedError

    def log_event(self, event: SecurityEvent) -> None:
        with self._lock:
            self._events.append(event)

    def get_events(self, limit: int = 100) -> list[SecurityEvent]:
        with self._lock:
            return self._events[-limit:]


class InputValidationLayer(SecurityLayer):
    _PATTERNS = [
        re.compile(r"<script[^>]*>", re.IGNORECASE),
        re.compile(r"javascript:", re.IGNORECASE),
        re.compile(r"on\w+\s*=", re.IGNORECASE),
    ]

    def __init__(self, max_length: int = 10000, max_depth: int = 10) -> None:
        super().__init__("input_validation")
        self.max_length = max_length
        self.max_depth = max_depth

    def check(self, data: Any, schema: Optional[dict] = None) -> tuple[bool, Optional[str]]:
        if isinstance(data, str):
            if len(data) > self.max_length:
                return False, "Input exceeds max length"
            for p in self._PATTERNS:
                if p.search(data):
                    self.log_event(SecurityEvent(self.name, "injection", SecurityLevel.HIGH, "Pattern detected"))
                    return False, "Injection detected"
        elif isinstance(data, dict):
            if self._get_depth(data) > self.max_depth:
                return False, "Input exceeds max depth"
        return True, None

    def _get_depth(self, obj: Any, current: int = 0) -> int:
        if current > self.max_depth:
            return current
        if isinstance(obj, dict):
            return max(self._get_depth(v, current + 1) for v in obj.values()) if obj else current
        elif isinstance(obj, (list, tuple)):
            return max(self._get_depth(v, current + 1) for v in obj) if obj else current
        return current


class AuthenticationLayer(SecurityLayer):
    def __init__(self) -> None:
        super().__init__("authentication")
        self._api_keys: dict[str, dict] = {}
        self._sessions: dict[str, dict] = {}

    def register_api_key(self, key: str, user_id: str, scopes: list[str] = None) -> None:
        with self._lock:
            self._api_keys[key] = {"user_id": user_id, "scopes": scopes or [], "created_at": time.monotonic()}

    def check(self, api_key: Optional[str] = None, session_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        if api_key:
            if api_key not in self._api_keys:
                return False, "Invalid API key"
            return True, None
        if session_id:
            if session_id not in self._sessions:
                return False, "Invalid session"
            return True, None
        return False, "No credentials"

    def create_session(self, user_id: str, ttl: int = 3600) -> str:
        session_id = secrets.token_urlsafe(32)
        with self._lock:
            self._sessions[session_id] = {"user_id": user_id, "created_at": time.monotonic(), "expires_at": time.monotonic() + ttl}
        return session_id


class AuthorizationLayer(SecurityLayer):
    def __init__(self) -> None:
        super().__init__("authorization")
        self._roles = {"admin": ["*"], "user": ["read", "write", "execute"], "guest": ["read"]}
        self._user_roles: dict[str, str] = {}

    def set_user_role(self, user_id: str, role: str) -> None:
        with self._lock:
            self._user_roles[user_id] = role

    def check(self, user_id: str, permission: str) -> tuple[bool, Optional[str]]:
        role = self._user_roles.get(user_id, "guest")
        perms = self._roles.get(role, [])
        if "*" in perms or permission in perms:
            return True, None
        return False, f"Permission denied: {permission}"


class SecurityManager:
    def __init__(self) -> None:
        self.layers: dict[str, SecurityLayer] = {}
        self._lock = threading.Lock()
        self._initialize_layers()

    def _initialize_layers(self) -> None:
        self.layers["input_validation"] = InputValidationLayer()
        self.layers["authentication"] = AuthenticationLayer()
        self.layers["authorization"] = AuthorizationLayer()

    def check_input(self, data: Any) -> tuple[bool, list[str]]:
        errors = []
        passed, error = self.layers["input_validation"].check(data)
        if not passed and error:
            errors.append(error)
        return len(errors) == 0, errors

    def authenticate(self, api_key: Optional[str] = None, session_id: Optional[str] = None) -> tuple[bool, Optional[str]]:
        return self.layers["authentication"].check(api_key=api_key, session_id=session_id)

    def authorize(self, user_id: str, permission: str) -> tuple[bool, Optional[str]]:
        return self.layers["authorization"].check(user_id, permission)


__all__ = ["SecurityLevel", "SecurityEvent", "SecurityLayer", "InputValidationLayer", "AuthenticationLayer", "AuthorizationLayer", "SecurityManager"]