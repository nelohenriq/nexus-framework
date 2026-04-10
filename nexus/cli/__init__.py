"""
NEXUS Framework - Command Line Interface

Provides nexus init and nexus run commands for easy project setup.
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

app = typer.Typer(
    name="nexus",
    help="NEXUS Framework - Unified Agentic Framework",
    add_completion=False,
)
console = Console()



@app.command()
def version():
    """Show NEXUS version."""
    from nexus import __version__
    console.print(f"NEXUS Framework v{__version__}")


@app.command()
def setup(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Interactive configuration wizard for NEXUS."""
    from nexus.cli.setup_wizard import run_setup
    config_path = str(config) if config else "nexus.yaml"
    console.print("[cyan]Starting NEXUS Setup Wizard...[/cyan]")
    if run_setup(config_path):
        console.print("[green]Configuration complete![/green]")
    else:
        console.print("[red]Configuration cancelled or failed.[/red]")
        raise typer.Exit(1)


# Provider command group
provider_app = typer.Typer(help="Manage LLM providers")
app.add_typer(provider_app, name="provider")


@provider_app.command("add")
def provider_add(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Add a new LLM provider with verification."""
    from nexus.cli.setup_wizard import add_provider
    config_path = str(config) if config else "nexus.yaml"
    console.print("[cyan]Add Provider Wizard[/cyan]")
    if add_provider(config_path):
        console.print("[green]Provider added successfully![/green]")
    else:
        console.print("[red]Provider addition cancelled or failed.[/red]")
        raise typer.Exit(1)


@provider_app.command("list")
def provider_list(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """List configured providers."""
    import os
    import yaml
    config_path = str(config) if config else "nexus.yaml"
    if not os.path.exists(config_path):
        console.print("[red]No configuration file found. Run nexus setup first.[/red]")
        raise typer.Exit(1)
    with open(config_path) as f:
        cfg = yaml.safe_load(f) or {}
    llm = cfg.get("llm", {})
    table = Table(title="Configured Provider")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Provider", llm.get("provider", "not set"))
    table.add_row("Model", llm.get("model", "not set"))
    table.add_row("API Base", llm.get("api_base", "not set"))
    console.print(table)


@provider_app.command("verify")
def provider_verify(
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Verify provider connectivity."""
    import os
    import yaml
    from nexus.cli.setup_wizard import ProviderVerifier
    config_path = str(config) if config else "nexus.yaml"
    if not os.path.exists(config_path):
        console.print("[red]No configuration file found.[/red]")
        raise typer.Exit(1)
    with open(config_path) as f:
        cfg = yaml.safe_load(f) or {}
    llm = cfg.get("llm", {})
    verifier = ProviderVerifier()
    success, message = verifier.verify_provider(
        provider=llm.get("provider"),
        api_key=llm.get("api_key"),
        api_base=llm.get("api_base"),
        model=llm.get("model")
    )
    if success:
        console.print(f"[green]{message}[/green]")
    else:
        console.print(f"[red]{message}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()