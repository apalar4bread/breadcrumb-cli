"""CLI commands for the flagger module."""
from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.flagger import FlagError, set_flag, clear_flag, get_flags, find_by_flag


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("flag")
def flag_cmd():
    """Manage step flags (todo, done, skip, review, warn)."""


@flag_cmd.command("set")
@click.argument("session_id")
@click.argument("step", type=int)
@click.argument("flag")
def set_cmd(session_id: str, step: int, flag: str):
    """Set FLAG on STEP (0-based) in SESSION_ID."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        set_flag(session, step, flag)
        store.save(session)
        click.echo(f"Flag '{flag}' set on step {step}.")
    except FlagError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@flag_cmd.command("clear")
@click.argument("session_id")
@click.argument("step", type=int)
@click.argument("flag")
def clear_cmd(session_id: str, step: int, flag: str):
    """Remove FLAG from STEP in SESSION_ID."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        clear_flag(session, step, flag)
        store.save(session)
        click.echo(f"Flag '{flag}' cleared from step {step}.")
    except FlagError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)


@flag_cmd.command("list")
@click.argument("session_id")
@click.argument("step", type=int)
def list_flags(session_id: str, step: int):
    """List flags on STEP in SESSION_ID."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    flags = get_flags(session, step)
    if flags:
        click.echo(", ".join(flags))
    else:
        click.echo("No flags set.")


@flag_cmd.command("find")
@click.argument("session_id")
@click.argument("flag")
def find_cmd(session_id: str, flag: str):
    """Find all steps in SESSION_ID carrying FLAG."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    indices = find_by_flag(session, flag)
    if indices:
        for i in indices:
            cmd = session.steps[i].command
            click.echo(f"  [{i}] {cmd}")
    else:
        click.echo(f"No steps flagged '{flag}'.")
