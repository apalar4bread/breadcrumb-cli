"""CLI commands for locking and unlocking sessions."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.locker import lock_session, unlock_session, list_locked, LockError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("lock")
def lock_cmd():
    """Lock or unlock sessions to prevent modification."""


@lock_cmd.command("add")
@click.argument("session_id")
def lock_add(session_id):
    """Lock a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        lock_session(session)
        store.save(session)
        click.echo(f"Session '{session.name}' is now locked.")
    except LockError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_cmd.command("remove")
@click.argument("session_id")
def lock_remove(session_id):
    """Unlock a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        unlock_session(session)
        store.save(session)
        click.echo(f"Session '{session.name}' is now unlocked.")
    except LockError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)


@lock_cmd.command("list")
def lock_list():
    """List all locked sessions."""
    store = _get_store()
    all_sessions = [store.load(sid) for sid in store.list_sessions()]
    locked = list_locked([s for s in all_sessions if s is not None])
    if not locked:
        click.echo("No locked sessions.")
        return
    for s in locked:
        click.echo(f"  [{s.id}] {s.name}")
