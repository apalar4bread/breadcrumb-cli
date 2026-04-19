"""CLI command for narrating a session."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.narrator import narrate_session, format_narration, NarratorError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("narrate")
def narrator_cmd():
    """Generate a human-readable narration of a session."""


@narrator_cmd.command("show")
@click.argument("session_id")
@click.option("--title", default="", help="Optional title for the narration.")
def show_narration(session_id: str, title: str):
    """Print a narration of all steps in a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        lines = narrate_session(session)
    except NarratorError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    label = title or session.name
    click.echo(format_narration(lines, title=label))
