"""CLI commands for rotating session steps."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.rotator import rotate_steps, format_rotate_result, RotateError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="rotate")
def rotate_cmd():
    """Rotate steps within a session."""


@rotate_cmd.command(name="left")
@click.argument("session_name")
@click.option("--positions", "-n", default=1, show_default=True, help="Number of positions to rotate.")
@click.option("--save", is_flag=True, default=False, help="Persist the rotated session.")
def rotate_left(session_name: str, positions: int, save: bool):
    """Rotate steps LEFT (forward) by N positions."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = rotate_steps(session, positions=positions, direction="left")
    except RotateError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if save:
        store.save(session)
        click.echo("Session saved.")
    click.echo(format_rotate_result(result))


@rotate_cmd.command(name="right")
@click.argument("session_name")
@click.option("--positions", "-n", default=1, show_default=True, help="Number of positions to rotate.")
@click.option("--save", is_flag=True, default=False, help="Persist the rotated session.")
def rotate_right(session_name: str, positions: int, save: bool):
    """Rotate steps RIGHT (backward) by N positions."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = rotate_steps(session, positions=positions, direction="right")
    except RotateError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    if save:
        store.save(session)
        click.echo("Session saved.")
    click.echo(format_rotate_result(result))
