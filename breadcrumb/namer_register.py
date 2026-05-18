"""Register the namer CLI command group."""

from __future__ import annotations

import click

from breadcrumb.session import Session
from breadcrumb.store import SessionStore
from breadcrumb.namer import NamerError, suggest_name, apply_suggested_name


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("name")
def namer_cmd() -> None:
    """Session naming utilities."""


@namer_cmd.command("suggest")
@click.argument("session_id")
def suggest_cmd(session_id: str) -> None:
    """Suggest a name for SESSION_ID based on its commands."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        name = suggest_name(session)
        click.echo(f"Suggested name: {name}")
    except NamerError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@namer_cmd.command("apply")
@click.argument("session_id")
@click.option("--force", is_flag=True, default=False, help="Override existing name.")
def apply_cmd(session_id: str, force: bool) -> None:
    """Auto-apply a suggested name to SESSION_ID."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    old_name = session.name
    new_name = apply_suggested_name(session, override=force)
    if new_name != old_name:
        store.save(session)
        click.echo(f"Renamed '{old_name}' -> '{new_name}'")
    else:
        click.echo(f"Name unchanged: '{old_name}'")


def register(cli: click.Group) -> None:
    """Attach namer_cmd to the root CLI group."""
    if "name" not in cli.commands:
        cli.add_command(namer_cmd)
