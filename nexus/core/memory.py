"""
NEXUS Framework - Memory Manager

SQLite-based persistent memory storage.
Optimized with thread-local connection pooling.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """A single memory entry."""
    key: str
    value: Any
    area: str = "main"
    created_at: float = field(default_factory=time.monotonic)
    updated_at: float = field(default_factory=time.monotonic)
    metadata: dict = field(default_factory=dict)


class MemoryManager:
    """
    SQLite-based memory manager.
    Thread-safe with WAL mode and connection pooling.
    """

    def __init__(self, db_path: str | Path = "nexus.db") -> None:
        self._db_path = Path(db_path)
        self._lock = threading.Lock()
        self._connections: dict[int, sqlite3.Connection] = {}
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local connection with pooling."""
        thread_id = threading.get_ident()
        if thread_id in self._connections:
            return self._connections[thread_id]
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.row_factory = sqlite3.Row
        self._connections[thread_id] = conn
        return conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        conn = self._get_connection()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                area TEXT DEFAULT "main",
                created_at REAL,
                updated_at REAL,
                metadata TEXT)
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_area ON memory(area)")
        conn.commit()

    def save(self, key: str, value: Any, area: str = "main", metadata: dict = None) -> None:
        """Save a value to memory."""
        with self._lock:
            now = time.monotonic()
            value_json = json.dumps(value)
            meta_json = json.dumps(metadata or {})
            conn = self._get_connection()
            conn.execute("""
                INSERT INTO memory (key, value, area, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at,
                    metadata = excluded.metadata
            """, (key, value_json, area, now, now, meta_json))
            conn.commit()

    def load(self, key: str, default: Any = None) -> Any:
        """Load a value from memory."""
        conn = self._get_connection()
        row = conn.execute("SELECT value FROM memory WHERE key = ?", (key,)).fetchone()
        if row:
            return json.loads(row["value"])
        return default

    def delete(self, key: str) -> bool:
        """Delete a value from memory."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.execute("DELETE FROM memory WHERE key = ?", (key,))
            conn.commit()
            return cursor.rowcount > 0

    def list_area(self, area: str) -> list[MemoryEntry]:
        """List all entries in an area."""
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM memory WHERE area = ?", (area,)).fetchall()
        return [MemoryEntry(
            key=r["key"],
            value=json.loads(r["value"]),
            area=r["area"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            metadata=json.loads(r["metadata"]))
            for r in rows]

    def clear_area(self, area: str) -> int:
        """Clear all entries in an area."""
        with self._lock:
            conn = self._get_connection()
            cursor = conn.execute("DELETE FROM memory WHERE area = ?", (area,))
            conn.commit()
            return cursor.rowcount

    def close(self) -> None:
        """Close all connections."""
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()


__all__ = ["MemoryEntry", "MemoryManager"]
