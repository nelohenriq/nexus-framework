"""CLI entry point for meta-agentic SDK."""

import typer
from pathlib import Path
from typing import Optional
import yaml

from meta_agents.config.loaders import load_meta_config, discover_agents, discover_skills, discover_projects
from meta_agents.backends.hermes_backend import HermesBackend

app = typer.Typer(name="meta-sdk", help="Meta-Agentic SDK CLI")


@app.command()
def init_project(
    name: str = typer.Argument(..., help="Name of the project to create"),
    force: bool = typer.Option(False, "--force", "-f", help="Allow initializing into a non-empty directory"),
) -> None:
    """Initialize a new meta project with default structure."""
    project_dir = Path(name)
    
    if project_dir.exists() and not force:
        if any(project_dir.iterdir()):
            typer.echo(f"Error: Directory '{name}' is not empty. Use --force to override.")
            raise typer.Exit(1)
    
    # Create directory structure
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create meta.yaml
    meta_config = {
        "version": "0.1",
        "default_backend": "hermes",
        "backends": {
            "hermes": {
                "home": "~/.hermes",
                "hermes_bin": "hermes"
            }
        }
    }
    with open(project_dir / "meta.yaml", "w") as f:
        yaml.dump(meta_config, f, default_flow_style=False)
    
    # Create agents directory with default agent
    agents_dir = project_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    
    default_agent = {
        "id": "default",
        "name": "Default Assistant",
        "role": "General-purpose assistant",
        "system_prompt": "You are a helpful, truthful assistant that uses installed skills when appropriate.",
        "skills": ["core/example-skill"],
        "tools": [],
        "project": "default",
        "model": "anthropic:opus",
        "security": {"name": "default"}
    }
    with open(agents_dir / "default.yaml", "w") as f:
        yaml.dump(default_agent, f, default_flow_style=False)
    
    # Create skills directory with example skill
    skills_dir = project_dir / "skills" / "core" / "example-skill"
    skills_dir.mkdir(parents=True, exist_ok=True)
    
    skill_md_content = """---
name: Example Skill
description: Basic example skill for demonstration.
tags: [demo, example]
requirements: []
---

# How to use Example Skill

This is just documentation. The agent reads this when it needs this skill.
"""
    with open(skills_dir / "SKILL.md", "w") as f:
        f.write(skill_md_content)
    
    # Create projects directory with default project
    projects_dir = project_dir / "projects" / "default"
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    default_project = {
        "id": "default",
        "name": "Default Project",
        "default_agent": "default"
    }
    with open(projects_dir / "config.yaml", "w") as f:
        yaml.dump(default_project, f, default_flow_style=False)
    
    # Create empty directories for knowledge, memory, secrets
    (project_dir / "knowledge").mkdir(exist_ok=True)
    (project_dir / "memory").mkdir(exist_ok=True)
    (project_dir / "secrets").mkdir(exist_ok=True)
    
    typer.echo(f"✓ Created meta project '{name}'")
    typer.echo(f" structure:")
    typer.echo(f" {name}/")
    typer.echo(f" ├── meta.yaml")
    typer.echo(f" ├── agents/")
    typer.echo(f" │ └── default.yaml")
    typer.echo(f" ├── skills/")
    typer.echo(f" │ └── core/example-skill/SKILL.md")
    typer.echo(f" ├── projects/")
    typer.echo(f" │ └── default/config.yaml")
    typer.echo(f" ├── knowledge/")
    typer.echo(f" ├── memory/")
    typer.echo(f" └── secrets/")


@app.command()
def sync(
    backend: str = typer.Argument("hermes", help="Backend to sync to"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Print planned actions without changing the system"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Log each resource as it is synced"),
) -> None:
    """Sync agents, skills, and projects to the backend."""
    # Find meta.yaml in current directory or parent
    meta_path = Path("meta.yaml")
    if not meta_path.exists():
        typer.echo("Error: meta.yaml not found in current directory")
        raise typer.Exit(1)
    
    root = meta_path.parent
    
    # Load configuration
    typer.echo(f"Loading configuration from {meta_path}...")
    try:
        config = load_meta_config(meta_path)
    except FileNotFoundError:
        typer.echo(f"Error: meta.yaml not found at {meta_path}")
        raise typer.Exit(1)
    
    if backend != "hermes":
        typer.echo(f"Error: Only 'hermes' backend is supported in v0")
        raise typer.Exit(1)
    
    if not config.backends.hermes:
        typer.echo("Error: Hermes backend not configured in meta.yaml")
        raise typer.Exit(1)
    
    # Discover resources
    agents = discover_agents(root)
    skills = discover_skills(root)
    projects = discover_projects(root)
    
    typer.echo(f"Discovered: {len(agents)} agents, {len(skills)} skills, {len(projects)} projects")
    
    if dry_run:
        typer.echo("\n[DRY RUN] Would sync:")
        for agent in agents:
            typer.echo(f" Agent: {agent.id} ({agent.name})")
        for skill in skills:
            typer.echo(f" Skill: {skill.id} ({skill.name})")
        for project in projects:
            typer.echo(f" Project: {project.id} ({project.name})")
        return
    
    # Create backend and sync
    hermes = HermesBackend(config.backends.hermes)
    
    if verbose:
        typer.echo("\nSyncing skills...")
        hermes.sync_skills(skills)
        for skill in skills:
            typer.echo(f" ✓ Skill: {skill.id}")
    else:
        hermes.sync_skills(skills)
    
    if verbose:
        typer.echo("\nSyncing agents...")
        hermes.sync_agents(agents)
        for agent in agents:
            typer.echo(f" ✓ Agent: {agent.id}")
    else:
        hermes.sync_agents(agents)
    
    if verbose:
        typer.echo("\nSyncing projects...")
        hermes.sync_projects(projects)
        for project in projects:
            typer.echo(f" ✓ Project: {project.id}")
    else:
        hermes.sync_projects(projects)
    
    typer.echo(f"\n✓ Synced {len(agents)} agents, {len(skills)} skills, {len(projects)} projects to Hermes.")


@app.command()
def doctor(
    backend: str = typer.Argument("hermes", help="Backend to check"),
) -> None:
    """Run diagnostics on the backend."""
    # Find meta.yaml
    meta_path = Path("meta.yaml")
    if not meta_path.exists():
        typer.echo("Error: meta.yaml not found in current directory")
        raise typer.Exit(1)
    
    root = meta_path.parent
    
    # Load configuration
    try:
        config = load_meta_config(meta_path)
    except FileNotFoundError:
        typer.echo(f"Error: meta.yaml not found at {meta_path}")
        raise typer.Exit(1)
    
    if backend != "hermes":
        typer.echo(f"Error: Only 'hermes' backend is supported in v0")
        raise typer.Exit(1)
    
    if not config.backends.hermes:
        typer.echo("Error: Hermes backend not configured in meta.yaml")
        raise typer.Exit(1)
    
    hermes = HermesBackend(config.backends.hermes)
    errors = []
    
    # Check Hermes home
    typer.echo("Checking Hermes home...")
    if hermes.verify_hermes_home():
        typer.echo(f" ✓ Hermes home exists at {hermes.home}")
    else:
        msg = f"✗ Hermes home not found at {hermes.home}"
        typer.echo(msg)
        errors.append(msg)
    
    # Check Hermes CLI
    typer.echo("Checking Hermes CLI...")
    if hermes.verify_hermes_cli():
        typer.echo(f" ✓ Hermes CLI available: {hermes.hermes_bin}")
    else:
        msg = f"✗ Hermes CLI not available: {hermes.hermes_bin}"
        typer.echo(msg)
        errors.append(msg)
    
    # Check skills
    typer.echo("Checking skills...")
    skills = discover_skills(root)
    for skill in skills:
        if hermes.verify_skill_exists(skill.id):
            typer.echo(f" ✓ Skill exists: {skill.id}")
        else:
            msg = f"✗ Skill not found in Hermes: {skill.id}"
            typer.echo(msg)
            errors.append(msg)
    
    # Check agents
    typer.echo("Checking agents...")
    agents = discover_agents(root)
    for agent in agents:
        issues = []
        if not agent.model:
            issues.append("model not set")
        for skill_id in agent.skills:
            if not hermes.verify_skill_exists(skill_id):
                issues.append(f"skill not found: {skill_id}")
        
        if issues:
            msg = f"✗ Agent {agent.id}: {', '.join(issues)}"
            typer.echo(msg)
            errors.append(msg)
        else:
            typer.echo(f" ✓ Agent valid: {agent.id}")
    
    # Summary
    typer.echo("")
    if errors:
        typer.echo(f"❌ {len(errors)} issue(s) found")
        raise typer.Exit(1)
    else:
        typer.echo("✅ All checks passed")


if __name__ == "__main__":
    app()
