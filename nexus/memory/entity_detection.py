"""Entity Detection Implementation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List
from datetime import datetime
import re
from enum import Enum


class EntityType(Enum):
    PERSON = "person"
    ORGANIZATION = "organization"
    EMAIL = "email"
    URL = "url"
    DATE = "date"
    TECHNOLOGY = "technology"
    MONEY = "money"
    PHONE = "phone"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls(value.lower())
        except ValueError:
            return cls.PERSON


@dataclass
class Entity:
    text: str
    entity_type: EntityType
    normalized: str = ""
    confidence: float = 1.0
    start: int = 0
    end: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "entity_type": self.entity_type.value,
            "normalized": self.normalized,
            "confidence": self.confidence
        }


@dataclass
class EntityDetectionResult:
    text: str
    entities: List[Entity]

    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        return [e for e in self.entities if e.entity_type == entity_type]


class EntityDetector:
    EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
    URL_PATTERN = re.compile(r"https?://[^\s]+")
    PHONE_PATTERN = re.compile(r"\+?[0-9]{10,15}")
    MONEY_PATTERN = re.compile(r"\$[0-9,]+(?:\.[0-9]{2})?")
    TECH_PATTERN = re.compile(r"\b(?:Python|JavaScript|TypeScript|Java|Docker|Kubernetes|AWS|GCP|Azure|OpenAI|Claude|GPT)\b", re.IGNORECASE)

    def detect(self, text: str) -> EntityDetectionResult:
        entities = []
        for match in self.EMAIL_PATTERN.finditer(text):
            entities.append(Entity(text=match.group(), entity_type=EntityType.EMAIL, normalized=match.group().lower(), start=match.start(), end=match.end()))
        for match in self.URL_PATTERN.finditer(text):
            entities.append(Entity(text=match.group(), entity_type=EntityType.URL, normalized=match.group(), start=match.start(), end=match.end()))
        for match in self.TECH_PATTERN.finditer(text):
            entities.append(Entity(text=match.group(), entity_type=EntityType.TECHNOLOGY, normalized=match.group().lower(), start=match.start(), end=match.end()))
        for match in self.MONEY_PATTERN.finditer(text):
            entities.append(Entity(text=match.group(), entity_type=EntityType.MONEY, normalized=match.group(), start=match.start(), end=match.end()))
        entities.sort(key=lambda e: e.start)
        return EntityDetectionResult(text=text, entities=entities)


def create_entity_detector() -> EntityDetector:
    return EntityDetector()


def detect_entities(text: str) -> EntityDetectionResult:
    return EntityDetector().detect(text)