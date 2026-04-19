"""CLI command: breadcrumb inspect <session_id> <step_index>"""

import click
from breadcrumb.store import SessionStore
from breadcrumb.inspector import inspect_step, format_inspection, InspectError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="inspect")
def inspect_cmd():
    """Inspect a single step in detail."""


@inspect_cmd.command(name="step")
@click.argument("session_id")
@click.argument("index", type=int)
def show_step(session_id: str, index: int):
    """Show detailed metadata for a step."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        insp = inspect_step(session, index)
        click.echo(format_inspection(insp))
    except InspectError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
