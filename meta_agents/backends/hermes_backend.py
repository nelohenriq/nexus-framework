"""Hermes backend implementation for meta-agentic SDK."""

from pathlib import Path
from typing import Iterable, Dict, Any
import shutil
import yaml
import subprocess
import sqlite3
import json

from meta_agents.models.agents import AgentDescriptor
from meta_agents.models.skills import SkillSpec
from meta_agents.models.projects import ProjectConfig
from meta_agents.models.memory import MemoryProvider, MemoryEvent, MemoryHit, ForgetCriteria
from meta_agents.config.meta_config import HermesBackendConfig


class HermesMemoryProvider:
    """Memory provider implementation for Hermes backend."""
    def __init__(self, hermes_home: Path, project_id: str):
        self.hermes_home = hermes_home
        self.project_id = project_id
        self.db_path = hermes_home / "meta" / "memory" / f"{project_id}.db"
        self._ensure_db()

    def _ensure_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def store(self, event: MemoryEvent) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS memory_events (
            id TEXT PRIMARY KEY, project_id TEXT, agent_id TEXT,
            session_id TEXT, timestamp REAL, content TEXT, metadata TEXT)""")
        cursor.execute("""INSERT OR REPLACE INTO memory_events
            (id, project_id, agent_id, session_id, timestamp, content, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (event.id, event.project_id, event.agent_id, event.session_id,
             event.timestamp, event.content, json.dumps(event.metadata)))
        conn.commit()
        conn.close()

    def search(self, query: str, *, filters: Dict[str, Any] | None = None) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql = "SELECT * FROM memory_events WHERE content LIKE ?"
        params = [f"%{query}%"]
        if filters:
            for key, value in filters.items():
                sql += f" AND {key} = ?"
                params.append(value)
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        results = []
        for row in rows:
            event = MemoryEvent(id=row[0], project_id=row[1], agent_id=row[2],
                               session_id=row[3], timestamp=row[4], content=row[5],
                               metadata=json.loads(row[6]) if row[6] else {})
            score = 1.0 if query.lower() in row[5].lower() else 0.5
            results.append(MemoryHit(event=event, score=score))
        return results

    def summarize_session(self, session_id: str) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM memory_events WHERE session_id = ? ORDER BY timestamp", (session_id,))
        rows = cursor.fetchall()
        conn.close()
        return "\n".join(row[0] for row in rows) if rows else ""

    def forget(self, criteria: ForgetCriteria) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        sql = "DELETE FROM memory_events WHERE 1=1"
        params = []
        if criteria.project_id:
            sql += " AND project_id = ?"
            params.append(criteria.project_id)
        if criteria.before_timestamp:
            sql += " AND timestamp < ?"
            params.append(criteria.before_timestamp)
        cursor.execute(sql, params)
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted


class HermesBackend:
    """Hermes backend implementation."""
    def __init__(self, config: HermesBackendConfig):
        self.config = config
        self.home = Path(config.home).expanduser()
        self.hermes_bin = config.hermes_bin or "hermes"
        self.meta_namespace = "meta"

    def _ensure_meta_dirs(self) -> None:
        (self.home / "meta" / "agents").mkdir(parents=True, exist_ok=True)
        (self.home / "meta" / "projects").mkdir(parents=True, exist_ok=True)
        (self.home / "skills" / self.meta_namespace).mkdir(parents=True, exist_ok=True)

    def sync_skills(self, skills: Iterable[SkillSpec]) -> None:
        self._ensure_meta_dirs()
        for skill in skills:
            skill_name = skill.id.split("/")[-1] if "/" in skill.id else skill.id
            target_dir = self.home / "skills" / self.meta_namespace / skill_name
            target_dir.mkdir(parents=True, exist_ok=True)
            target_file = target_dir / "SKILL.md"
            shutil.copy2(skill.path, target_file)

    def sync_agents(self, agents: Iterable[AgentDescriptor]) -> None:
        self._ensure_meta_dirs()
        for agent in agents:
            agent_file = self.home / "meta" / "agents" / f"{agent.id}.yaml"
            agent_data = {"id": agent.id, "name": agent.name, "role": agent.role,
                         "system_prompt": agent.system_prompt, "skills": agent.skills,
                         "tools": agent.tools, "project": agent.project, "model": agent.model}
            if agent.security:
                agent_data["security"] = {"name": agent.security.name}
            with open(agent_file, "w") as f:
                yaml.dump(agent_data, f, default_flow_style=False)

    def sync_projects(self, projects: Iterable[ProjectConfig]) -> None:
        self._ensure_meta_dirs()
        for project in projects:
            project_file = self.home / "meta" / "projects" / f"{project.id}.yaml"
            project_data = {"id": project.id, "name": project.name,
                           "meta_project_path": str(project.path), "default_agent": project.default_agent}
            with open(project_file, "w") as f:
                yaml.dump(project_data, f, default_flow_style=False)

    def get_memory_provider(self, project_id: str) -> MemoryProvider:
        return HermesMemoryProvider(self.home, project_id)

    def verify_hermes_cli(self) -> bool:
        try:
            result = subprocess.run([self.hermes_bin, "--version"], capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def verify_hermes_home(self) -> bool:
        return self.home.exists()

    def verify_skill_exists(self, skill_id: str) -> bool:
        skill_name = skill_id.split("/")[-1] if "/" in skill_id else skill_id
        skill_path = self.home / "skills" / self.meta_namespace / skill_name / "SKILL.md"
        return skill_path.exists()
