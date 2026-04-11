"""NEXUS Framework - Anti-Corruption Layer Module

Translates external framework patterns to NEXUS native format.
"""

from .acl import (
    TranslationResult,
    AntiCorruptionLayer,
    HermesACL,
    AgentZeroACL,
    OpenClawACL,
    OpenFangACL,
    ACLRegistry
)

__all__ = [
    "TranslationResult",
    "AntiCorruptionLayer",
    "HermesACL",
    "AgentZeroACL",
    "OpenClawACL",
    "OpenFangACL",
    "ACLRegistry"
]