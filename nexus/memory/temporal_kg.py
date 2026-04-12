"""Temporal Knowledge Graph Implementation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, date
from enum import Enum
import sqlite3
import hashlib


class FactStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


class RelationType(Enum):
    IS_A = "is_a"
    HAS_A = "has_a"
    RELATED_TO = "related_to"
    CAUSES = "causes"
    WORKS_FOR = "works_for"


@dataclass(slots=True)
class TemporalFact:
    id: str
    subject: str
    predicate: str
    object: str
    value: Any = None
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    confidence: float = 1.0
    status: FactStatus = FactStatus.ACTIVE
    source: str = ""

    def is_active(self, query_date=None):
        if query_date is None:
            query_date = date.today()
        if self.status != FactStatus.ACTIVE:
            return False
        if self.start_date > query_date:
            return False
        if self.end_date is not None and self.end_date < query_date:
            return False
        return True


@dataclass(slots=True)
class Entity:
    name: str
    entity_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    facts: List[str] = field(default_factory=list)


class TemporalKnowledgeGraph:
    def __init__(self, db_path=None):
        self.db_path = db_path or ":memory:"
        self._init_db()
        self.entities = {}
        self.facts = {}

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS facts (id TEXT PRIMARY KEY, subject TEXT NOT NULL, predicate TEXT NOT NULL, object TEXT NOT NULL, value TEXT, start_date TEXT NOT NULL, end_date TEXT, confidence REAL DEFAULT 1.0, status TEXT DEFAULT 'active')")
        conn.commit()
        conn.close()

    def add_fact(self, subject, predicate, object_val, value=None, start_date=None, confidence=1.0, source=""):
        fact_id = hashlib.md5(f"{subject}:{predicate}:{object_val}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        fact = TemporalFact(id=fact_id, subject=subject, predicate=predicate, object=object_val, value=value, start_date=start_date or date.today(), confidence=confidence, source=source)
        self.facts[fact_id] = fact
        if subject not in self.entities:
            self.entities[subject] = Entity(name=subject, entity_type="unknown")
        self.entities[subject].facts.append(fact_id)
        return fact

    def query(self, subject=None, predicate=None, object_val=None, include_expired=False):
        results = []
        facts = self.facts
        for fact in facts.values():
            if subject and fact.subject != subject:
                continue
            if predicate and fact.predicate != predicate:
                continue
            if object_val and fact.object != object_val:
                continue
            if not include_expired and not fact.is_active():
                continue
            results.append(fact)
        return results


def create_temporal_kg(db_path=None):
    return TemporalKnowledgeGraph(db_path=db_path)