"""cli_stamper.py — CLI commands for stamping steps."""
from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.stamper import StampError, stamp_step, clear_stamp, list_stamped, get_stamp


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("stamp")
def stamp_cmd() -> None:
    """Attach or query time stamps on session steps."""


@stamp_cmd.command("add")
@click.argument("session_name")
@click.argument("index", type=int)
@click.option("--label", "-l", default="", help="Optional label for the stamp.")
def add_stamp(session_name: str, index: int, label: str) -> None:
    """Stamp step INDEX in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        step = stamp_step(session, index, label)
    except StampError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    store.save(session)
    ts = step.metadata["stamped_at"]
    msg = f"Stamped step {index} at {ts}"
    if label:
        msg += f" [{label}]"
    click.echo(msg)


@stamp_cmd.command("remove")
@click.argument("session_name")
@click.argument("index", type=int)
def remove_stamp(session_name: str, index: int) -> None:
    """Remove stamp from step INDEX in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        clear_stamp(session, index)
    except StampError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    store.save(session)
    click.echo(f"Stamp removed from step {index}.")


@stamp_cmd.command("list")
@click.argument("session_name")
def list_stamps(session_name: str) -> None:
    """List all stamped steps in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    entries = list_stamped(session)
    if not entries:
        click.echo("No stamped steps.")
        return
    for idx, step in entries:
        ts = get_stamp(step)
        label = step.metadata.get("stamp_label", "")
        suffix = f" [{label}]" if label else ""
        click.echo(f"  [{idx}] {step.command}  @ {ts}{suffix}")
