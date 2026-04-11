#!/usr/bin/env python3
"""NEXUS Framework - Event Sourcing

Full audit trail and event replay capabilities for agents.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class Event:
    event_id: str
    event_type: str
    timestamp: datetime
    aggregate_id: str
    aggregate_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass
class EventStoreConfig:
    db_path: str = ":memory:"
    batch_size: int = 100
    retention_days: int = 90


class EventStore:
    """SQLite-based event store for audit trail."""

    CREATE_TABLE_SQL = """
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            aggregate_id TEXT NOT NULL,
            aggregate_type TEXT NOT NULL,
            data TEXT NOT NULL,
            metadata TEXT,
            version INTEGER DEFAULT 1
        )
    """

    def __init__(self, config: Optional[EventStoreConfig] = None):
        self._config = config or EventStoreConfig()
        self._db = self._init_db()

    def _init_db(self) -> sqlite3.Connection:
        db = sqlite3.connect(self._config.db_path)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        cursor.execute(self.CREATE_TABLE_SQL)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_aggregate ON events(aggregate_id, aggregate_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
        db.commit()
        return db

    def append(self, event: Event) -> None:
        cursor = self._db.cursor()
        cursor.execute(
            "INSERT INTO events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event.event_id, event.event_type, event.timestamp.isoformat(),
                event.aggregate_id, event.aggregate_type,
                json.dumps(event.data), json.dumps(event.metadata), event.version)
        )
        self._db.commit()

    def get_events(self, aggregate_id: str) -> List[Event]:
        cursor = self._db.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE aggregate_id = ? ORDER BY timestamp",
            (aggregate_id,)
        )
        return [self._row_to_event(row) for row in cursor.fetchall()]

    def get_events_by_type(self, event_type: str) -> List[Event]:
        cursor = self._db.cursor()
        cursor.execute(
            "SELECT * FROM events WHERE event_type = ? ORDER BY timestamp",
            (event_type,)
        )
        return [self._row_to_event(row) for row in cursor.fetchall()]

    def get_all_events(self, limit: int = 1000) -> List[Event]:
        cursor = self._db.cursor()
        cursor.execute("SELECT * FROM events ORDER BY timestamp DESC LIMIT ?", (limit,))
        return [self._row_to_event(row) for row in cursor.fetchall()]

    def _row_to_event(self, row: sqlite3.Row) -> Event:
        return Event(
            event_id=row[0],
            event_type=row[1],
            timestamp=datetime.fromisoformat(row[2]),
            aggregate_id=row[3],
            aggregate_type=row[4],
            data=json.loads(row[5]),
            metadata=json.loads(row[6]) if row[6] else {},
            version=row[7]
        )

    def close(self) -> None:
        self._db.close()


class EventSourcing:
    """Event sourcing manager for agents."""

    def __init__(self, store: Optional[EventStore] = None):
        self._store = store or EventStore()
        self._handlers: Dict[str, Callable] = {}

    def register_handler(self, event_type: str, handler: Callable) -> None:
        self._handlers[event_type] = handler

    def emit(self, event_type: str, aggregate_id: str, aggregate_type: str,
        data: Dict[str, Any], metadata: Optional[Dict] = None) -> Event:
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            timestamp=datetime.utcnow(),
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            data=data,
            metadata=metadata or {}
        )
        self._store.append(event)
        if event_type in self._handlers:
            self._handlers[event_type](event)
        return event

    def replay(self, aggregate_id: str) -> Dict[str, Any]:
        events = self._store.get_events(aggregate_id)
        state = {}
        for event in events:
            if event.event_type in self._handlers:
                self._handlers[event.event_type](event)
            state.update(event.data)
        return state

    def get_audit_trail(self, aggregate_id: str) -> List[Dict]:
        events = self._store.get_events(aggregate_id)
        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
                "data": e.data
            }
        for e in events
        ]


# Default instances
event_store = EventStore()
event_sourcing = EventSourcing(event_store)


__all__ = ["Event", "EventStoreConfig", "EventStore", "EventSourcing", "event_store", "event_sourcing"]