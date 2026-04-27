"""cli_cursor.py — CLI commands for managing the session cursor."""

import click
from breadcrumb.store import SessionStore
from breadcrumb import cursor as cur


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("cursor", help="Track and move a cursor through session steps.")
def cursor_cmd():
    pass


@cursor_cmd.command("set")
@click.argument("session_name")
@click.argument("index", type=int)
def set_pos(session_name: str, index: int):
    """Set the cursor to STEP INDEX (0-based) in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = cur.set_cursor(session, index)
        store.save(session)
        click.echo(str(result))
    except cur.CursorError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cursor_cmd.command("get")
@click.argument("session_name")
def get_pos(session_name: str):
    """Show the current cursor position for SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = cur.get_cursor(session)
        click.echo(str(result))
        if cur.is_at_end(session):
            click.echo("(at end)")
    except cur.CursorError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cursor_cmd.command("advance")
@click.argument("session_name")
@click.option("--by", default=1, show_default=True, help="Number of steps to advance.")
def advance(session_name: str, by: int):
    """Advance the cursor forward in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = cur.advance_cursor(session, by=by)
        store.save(session)
        click.echo(str(result))
    except cur.CursorError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@cursor_cmd.command("reset")
@click.argument("session_name")
def reset(session_name: str):
    """Clear the cursor position for SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    cur.reset_cursor(session)
    store.save(session)
    click.echo(f"Cursor reset for '{session_name}'.")
