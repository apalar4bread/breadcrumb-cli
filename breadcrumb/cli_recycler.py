"""cli_recycler.py — CLI commands for the recycle bin."""
from __future__ import annotations

import click

from breadcrumb.recycler import (
    format_recycle_entry,
    format_recycle_list,
    recycle_session,
    restore_session,
)
from breadcrumb.recycle_store import RecycleStore
from breadcrumb.store import SessionStore


def _get_stores():
    return SessionStore(), RecycleStore()


@click.group("recycle")
def recycle_cmd():
    """Manage the recycle bin (soft-delete / restore)."""


@recycle_cmd.command("delete")
@click.argument("session_id")
@click.option("--reason", default="", help="Optional reason for deletion.")
def delete_cmd(session_id: str, reason: str):
    """Move a session to the recycle bin."""
    store, rstore = _get_stores()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    entry = recycle_session(session, reason=reason)
    rstore.save(entry)
    store.delete(session_id)
    click.echo(f"Session '{session.name}' moved to recycle bin.")


@recycle_cmd.command("restore")
@click.argument("session_id")
def restore_cmd(session_id: str):
    """Restore a session from the recycle bin."""
    store, rstore = _get_stores()
    entry = rstore.load(session_id)
    session = restore_session(entry)
    store.save(session)
    rstore.delete(session_id)
    click.echo(f"Session '{session.name}' restored.")


@recycle_cmd.command("list")
def list_cmd():
    """List all sessions in the recycle bin."""
    _, rstore = _get_stores()
    entries = rstore.list_entries()
    click.echo(format_recycle_list(entries))


@recycle_cmd.command("info")
@click.argument("session_id")
def info_cmd(session_id: str):
    """Show details of a recycled session."""
    _, rstore = _get_stores()
    entry = rstore.load(session_id)
    click.echo(format_recycle_entry(entry))


@recycle_cmd.command("purge")
@click.confirmation_option(prompt="Permanently delete all recycled sessions?")
def purge_cmd():
    """Permanently delete all recycled sessions."""
    _, rstore = _get_stores()
    count = rstore.purge()
    click.echo(f"Purged {count} session(s) from recycle bin.")
