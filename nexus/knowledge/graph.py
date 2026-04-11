#!/usr/bin/env python3
"""
NEXUS Framework - Knowledge Graph

Entity relationship storage and querying system.
Provides graph-based memory with semantic relationships.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from enum import Enum


class RelationType(str, Enum):
    RELATES_TO = "relates_to"
    DEPENDS_ON = "depends_on"
    IMPLEMENTED_BY = "implemented_by"
    FOLLOWS = "follows"
    CONTRADICTS = "contradicts"
    SUPPORTS = "supports"
    USES = "uses"
    PRODUCES = "produces"


@dataclass
class Entity:
    id: str
    type: str
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class Relation:
    source_id: str
    target_id: str
    relation_type: RelationType
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeGraph:
    """SQLite-backed knowledge graph for entity relationships."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path(":memory:")
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS entities (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                properties TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS relations (
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relation_type TEXT NOT NULL,
                properties TEXT,
                weight REAL DEFAULT 1.0,
                created_at TEXT,
                PRIMARY KEY (source_id, target_id, relation_type)
            );
            CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type);
            CREATE INDEX IF NOT EXISTS idx_relations_source ON relations(source_id);
            CREATE INDEX IF NOT EXISTS idx_relations_target ON relations(target_id);
        """)
        conn.commit()

    def add_entity(self, entity: Entity) -> None:
        conn = self._get_conn()
        conn.execute("""
            INSERT OR REPLACE INTO entities
            (id, type, name, properties, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entity.id, entity.type, entity.name,
            json.dumps(entity.properties),
            entity.created_at.isoformat(),
            entity.updated_at.isoformat()
        ))
        conn.commit()

    def get_entity(self, entity_id: str) -> Optional[Entity]:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT * FROM entities WHERE id = ?", (entity_id,)
        ).fetchone()
        if row:
            return Entity(
                id=row["id"],
                type=row["type"],
                name=row["name"],
                properties=json.loads(row["properties"] or "{}"),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"])
            )
        return None

    def add_relation(self, relation: Relation) -> None:
        conn = self._get_conn()
        conn.execute("""
            INSERT OR REPLACE INTO relations
            (source_id, target_id, relation_type, properties, weight, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            relation.source_id, relation.target_id,
            relation.relation_type.value,
            json.dumps(relation.properties),
            relation.weight,
            relation.created_at.isoformat()
        ))
        conn.commit()

    def get_relations(
        self,
        entity_id: str,
        relation_type: Optional[RelationType] = None,
        direction: str = "outgoing"
    ) -> List[Relation]:
        conn = self._get_conn()
        if direction == "outgoing":
            query = "SELECT * FROM relations WHERE source_id = ?"
            params: List[Any] = [entity_id]
        elif direction == "incoming":
            query = "SELECT * FROM relations WHERE target_id = ?"
            params = [entity_id]
        else:
            query = "SELECT * FROM relations WHERE source_id = ? OR target_id = ?"
            params = [entity_id, entity_id]
        if relation_type:
            query += " AND relation_type = ?"
            params.append(relation_type.value)
        rows = conn.execute(query, params).fetchall()
        return [self._row_to_relation(row) for row in rows]

    def _row_to_relation(self, row: sqlite3.Row) -> Relation:
        return Relation(
            source_id=row["source_id"],
            target_id=row["target_id"],
            relation_type=RelationType(row["relation_type"]),
            properties=json.loads(row["properties"] or "{}"),
            weight=row["weight"],
            created_at=datetime.fromisoformat(row["created_at"])
        )

    def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> List[List[str]]:
        paths: List[List[str]] = []
        queue: List[Tuple[str, List[str]]] = [(source_id, [source_id])]
        visited: Set[str] = {source_id}
        while queue and len(paths) < 10:
            current, path = queue.pop(0)
            if current == target_id:
                paths.append(path)
                continue
            if len(path) >= max_depth:
                continue
            for relation in self.get_relations(current):
                next_id = relation.target_id
                if next_id not in visited:
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))
        return paths

    def get_stats(self) -> Dict[str, int]:
        conn = self._get_conn()
        entity_count = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        relation_count = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
        return {"entities": entity_count, "relations": relation_count}


__all__ = ["KnowledgeGraph", "Entity", "Relation", "RelationType"]