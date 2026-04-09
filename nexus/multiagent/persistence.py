from __future__ import annotations
import json
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
import zlib


@dataclass(slots=True)
class AgentState:
    agent_id: str
    name: str
    status: str
    context: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    saved_at: float = field(default_factory=time.monotonic)

    def to_dict(self) -> dict[str, Any]:
        d = {}
        d["agent_id"] = self.agent_id
        d["name"] = self.name
        d["status"] = self.status
        d["context"] = self.context
        d["metadata"] = self.metadata
        d["saved_at"] = self.saved_at
        return d


@dataclass(slots=True)
class WorkflowState:
    workflow_id: str
    name: str
    status: str
    steps: list[dict[str, Any]]
    current_step: int
    results: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.monotonic)
    updated_at: float = field(default_factory=time.monotonic)


class PersistenceManager:
    def __init__(self, db_path: str = "nexus_persistence.db") -> None:
        self.db_path = Path(db_path)
        self._connections = {}
        self._lock = threading.RLock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        thread_id = threading.get_ident()
        if thread_id in self._connections:
            return self._connections[thread_id]
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        self._connections[thread_id] = conn
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        conn.execute("CREATE TABLE IF NOT EXISTS agent_states (agent_id TEXT PRIMARY KEY, name TEXT, status TEXT, context BLOB, metadata BLOB, saved_at REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS workflow_states (workflow_id TEXT PRIMARY KEY, name TEXT, status TEXT, steps BLOB, current_step INTEGER, results BLOB, created_at REAL, updated_at REAL)")
        conn.execute("CREATE TABLE IF NOT EXISTS checkpoints (checkpoint_id TEXT PRIMARY KEY, agent_id TEXT, workflow_id TEXT, state BLOB, created_at REAL)")
        conn.commit()

    def save_agent_state(self, state: AgentState) -> bool:
        conn = self._get_connection()
        context_blob = zlib.compress(json.dumps(state.context).encode())
        metadata_blob = zlib.compress(json.dumps(state.metadata).encode())
        with self._lock:
            conn.execute("INSERT OR REPLACE INTO agent_states VALUES (?, ?, ?, ?, ?, ?)", (state.agent_id, state.name, state.status, context_blob, metadata_blob, state.saved_at))
            conn.commit()
        return True

    def load_agent_state(self, agent_id: str) -> Optional[AgentState]:
        conn = self._get_connection()
        with self._lock:
            row = conn.execute("SELECT * FROM agent_states WHERE agent_id = ?", (agent_id,)).fetchone()
            if not row: return None
            context = json.loads(zlib.decompress(row["context"]).decode())
            metadata = json.loads(zlib.decompress(row["metadata"]).decode())
            return AgentState(row["agent_id"], row["name"], row["status"], context, metadata, row["saved_at"])

    def create_checkpoint(self, agent_id: str, workflow_id: str, state: dict) -> str:
        import uuid
        checkpoint_id = str(uuid.uuid4())
        conn = self._get_connection()
        state_blob = zlib.compress(json.dumps(state).encode())
        with self._lock:
            conn.execute("INSERT INTO checkpoints VALUES (?, ?, ?, ?, ?)", (checkpoint_id, agent_id, workflow_id, state_blob, time.monotonic()))
            conn.commit()
        return checkpoint_id

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[dict]:
        conn = self._get_connection()
        with self._lock:
            row = conn.execute("SELECT state FROM checkpoints WHERE checkpoint_id = ?", (checkpoint_id,)).fetchone()
            if not row: return None
            return json.loads(zlib.decompress(row["state"]).decode())

    def close(self) -> None:
        with self._lock:
            for conn in self._connections.values():
                conn.close()
            self._connections.clear()