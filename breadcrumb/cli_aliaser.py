"""CLI commands for managing session aliases."""

from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.aliaser import (
    AliasError,
    set_alias,
    clear_alias,
    get_alias,
    find_by_alias,
    list_aliases,
)


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("alias")
def alias_cmd() -> None:
    """Manage short aliases for sessions."""


@alias_cmd.command("set")
@click.argument("session_name")
@click.argument("alias")
def set_cmd(session_name: str, alias: str) -> None:
    """Assign ALIAS to SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        raise click.ClickException(f"Session '{session_name}' not found.")
    try:
        result = set_alias(session, alias)
        store.save(session)
        click.echo(f"Alias '{result}' set for session '{session.name}'.")
    except AliasError as exc:
        raise click.ClickException(str(exc)) from exc


@alias_cmd.command("clear")
@click.argument("session_name")
def clear_cmd(session_name: str) -> None:
    """Remove the alias from SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        raise click.ClickException(f"Session '{session_name}' not found.")
    clear_alias(session)
    store.save(session)
    click.echo(f"Alias cleared for session '{session.name}'.")


@alias_cmd.command("get")
@click.argument("session_name")
def get_cmd(session_name: str) -> None:
    """Print the alias for SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        raise click.ClickException(f"Session '{session_name}' not found.")
    alias = get_alias(session)
    if alias:
        click.echo(alias)
    else:
        click.echo(f"No alias set for '{session.name}'.")


@alias_cmd.command("find")
@click.argument("alias")
def find_cmd(alias: str) -> None:
    """Find the session that owns ALIAS."""
    store = _get_store()
    sessions = [store.load(n) for n in store.list_sessions()]
    sessions = [s for s in sessions if s is not None]
    match = find_by_alias(sessions, alias)
    if match:
        click.echo(match.name)
    else:
        click.echo(f"No session found with alias '{alias}'.")


@alias_cmd.command("list")
def list_cmd() -> None:
    """List all aliases across all sessions."""
    store = _get_store()
    sessions = [store.load(n) for n in store.list_sessions()]
    sessions = [s for s in sessions if s is not None]
    mapping = list_aliases(sessions)
    if not mapping:
        click.echo("No aliases defined.")
        return
    for alias, name in sorted(mapping.items()):
        click.echo(f"{alias:<20} -> {name}")
