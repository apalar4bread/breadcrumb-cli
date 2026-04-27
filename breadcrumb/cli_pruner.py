"""CLI commands for pruning session steps."""

from __future__ import annotations

import click

from breadcrumb.pruner import PruneError, prune_beyond_count, prune_empty_commands, prune_older_than
from breadcrumb.store import SessionStore


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("prune")
def prune_cmd():
    """Prune steps from a session."""


@prune_cmd.command("old")
@click.argument("session_name")
@click.argument("days", type=int)
@click.option("--save", is_flag=True, default=False, help="Persist changes.")
def prune_old(session_name: str, days: int, save: bool):
    """Remove steps older than DAYS days from SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = prune_older_than(session, days=days)
    except PruneError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if save:
        store.save(session)
        click.echo(f"Saved. {result.summary()}")
    else:
        click.echo(f"[dry-run] {result.summary()}")


@prune_cmd.command("cap")
@click.argument("session_name")
@click.argument("max_steps", type=int)
@click.option("--save", is_flag=True, default=False, help="Persist changes.")
def prune_cap(session_name: str, max_steps: int, save: bool):
    """Keep only the MAX_STEPS most recent steps in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = prune_beyond_count(session, max_steps=max_steps)
    except PruneError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if save:
        store.save(session)
        click.echo(f"Saved. {result.summary()}")
    else:
        click.echo(f"[dry-run] {result.summary()}")


@prune_cmd.command("blanks")
@click.argument("session_name")
@click.option("--save", is_flag=True, default=False, help="Persist changes.")
def prune_blanks(session_name: str, save: bool):
    """Remove steps with empty or whitespace-only commands from SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    result = prune_empty_commands(session)
    if save:
        store.save(session)
        click.echo(f"Saved. {result.summary()}")
    else:
        click.echo(f"[dry-run] {result.summary()}")
