"""Setup Wizard for TUI Configuration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum


class WizardStep(Enum):
    WELCOME = "welcome"
    PROVIDER = "provider"
    API_KEY = "api_key"
    MODEL = "model"
    FEATURES = "features"
    COMPLETE = "complete"


@dataclass(slots=True)
class WizardConfig:
    provider: str = ""
    api_key: str = ""
    model: str = ""
    features: List[str] = field(default_factory=list)
    advanced: Dict[str, Any] = field(default_factory=dict)


class SetupWizard:
    def __init__(self):
        self.current_step = WizardStep.WELCOME
        self.config = WizardConfig()
        self.steps = list(WizardStep)
        self.validators = {}

    def next_step(self) -> Optional[WizardStep]:
        idx = self.steps.index(self.current_step)
        if idx < len(self.steps) - 1:
            self.current_step = self.steps[idx + 1]
            return self.current_step
        return None

    def prev_step(self) -> Optional[WizardStep]:
        idx = self.steps.index(self.current_step)
        if idx > 0:
            self.current_step = self.steps[idx - 1]
            return self.current_step
        return None

    def set_value(self, key: str, value: Any):
        if hasattr(self.config, key):
            setattr(self.config, key, value)

    def validate(self) -> bool:
        return bool(self.config.provider and self.config.api_key)

    def get_config(self) -> Dict[str, Any]:
        return {"provider": self.config.provider, "model": self.config.model, "features": self.config.features, "advanced": self.config.advanced}


def create_setup_wizard() -> SetupWizard:
    return SetupWizard()