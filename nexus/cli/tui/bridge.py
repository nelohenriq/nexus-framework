"""Python-TypeScript Bridge for OpenTUI Integration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import subprocess
import json
import os


@dataclass(slots=True)
class TUIEvent:
    event_type: str
    data: Dict[str, Any]
    timestamp: str


@dataclass(slots=True)
class TUIConfig:
    theme: str = "dark"
    colors: Dict[str, str] = field(default_factory=lambda: {"primary": "#4A90D9", "secondary": "#6C7A89", "accent": "#F39C12", "background": "#1E1E1E", "text": "#FFFFFF"})
    layout: str = "default"


class OpenTUIBridge:
    def __init__(self, tui_path: Optional[str] = None):
        self.tui_path = tui_path or os.path.expanduser("~/.opentui")
        self.event_handlers = {}
        self._process = None

    def is_available(self) -> bool:
        return os.path.exists(self.tui_path)

    def start_tui(self, component: str = "dashboard") -> bool:
        if not self.is_available():
            return False
        try:
            self._process = subprocess.Popen(["node", f"{self.tui_path}/bin/opentui", component], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception:
            return False

    def stop_tui(self):
        if self._process:
            self._process.terminate()
            self._process = None

    def send_event(self, event: TUIEvent) -> bool:
        if self._process and self._process.stdin:
            try:
                self._process.stdin.write(json.dumps({"type": event.event_type, "data": event.data, "timestamp": event.timestamp}) + "\n")
                self._process.stdin.flush()
                return True
            except Exception:
                return False
        return False

    def on_event(self, event_type: str, handler):
        self.event_handlers[event_type] = handler


def create_bridge(tui_path: Optional[str] = None) -> OpenTUIBridge:
    return OpenTUIBridge(tui_path=tui_path)