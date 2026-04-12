"""TUI Module - OpenTUI Integration."""

from .bridge import (
    TUIEvent, TUIConfig, OpenTUIBridge,
    create_bridge
)
from .dashboard import (
    AgentStatus, MetricCard, DashboardData,
    create_dashboard
)
from .wizard import (
    WizardStep, WizardConfig, SetupWizard,
    create_setup_wizard
)
from .monitor import (
    MonitorEvent, RealtimeMonitor,
    create_monitor
)
from .automation import (
    AutomationTask, AutomationResult, AIAutomation,
    create_automation
)

__all__ = [
    "TUIEvent", "TUIConfig", "OpenTUIBridge", "create_bridge",
    "AgentStatus", "MetricCard", "DashboardData", "create_dashboard",
    "WizardStep", "WizardConfig", "SetupWizard", "create_setup_wizard",
    "MonitorEvent", "RealtimeMonitor", "create_monitor",
    "AutomationTask", "AutomationResult", "AIAutomation", "create_automation"
]