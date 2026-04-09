"""
NEXUS Framework - Memory Manager

SQLite-based persistent memory storage.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """A single memory entry."""
    key: str
    value: Any
    area: str = "main"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class MemoryManager:
    """
    SQLite-based memory manager.
    Thread-safe with WAL mode for concurrency.
    """

    def __init__(self, db_path: str | Path = "nexus.db") -> None:
        self._db_path = Path(db_path)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with self._get_connection() as conn:
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

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection with WAL mode."""
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.row_factory = sqlite3.Row
        return conn

    def save(self, key: str, value: Any, area: str = "main", metadata: dict = None) -> None:
        """Save a value to memory."""
        with self._lock:
            now = time.time()
            value_json = json.dumps(value)
            meta_json = json.dumps(metadata or {})
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO memory (key, value, area, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                     value = excluded.value,
                     updated_at = excluded.updated_at,
                     metadata = excluded.metadata
                """, (key, value_json, area, now, now, meta_json))

    def load(self, key: str, default: Any = None) -> Any:
        """Load a value from memory."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM memory WHERE key = ?", (key,)).fetchone()
            if row:
                return json.loads(row["value"])
            return default

    def delete(self, key: str) -> bool:
        """Delete a value from memory."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM memory WHERE key = ?", (key,))
                return cursor.rowcount > 0

    def list_area(self, area: str) -> list[MemoryEntry]:
        """List all entries in an area."""
        with self._get_connection() as conn:
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
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM memory WHERE area = ?", (area,))
                return cursor.rowcount


__all__ = ["MemoryEntry", "MemoryManager"]
