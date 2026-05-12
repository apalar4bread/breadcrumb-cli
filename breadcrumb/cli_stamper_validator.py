"""CLI command for validating stamps in a session."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.stamper_validator import validate_stamps, format_stamp_validation


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("stamp-validate")
def stamp_validate_cmd():
    """Validate stamp metadata across session steps."""


@stamp_validate_cmd.command("check")
@click.argument("session_name")
def check_stamps(session_name: str):
    """Check all stamps in SESSION_NAME for validity."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    result = validate_stamps(session)
    click.echo(format_stamp_validation(result))

    if not result:
        raise SystemExit(2)


@stamp_validate_cmd.command("check-all")
def check_all_stamps():
    """Check stamps across all sessions."""
    store = _get_store()
    sessions = store.list_sessions()

    if not sessions:
        click.echo("No sessions found.")
        return

    any_failed = False
    for name in sessions:
        session = store.load(name)
        if session is None:
            continue
        result = validate_stamps(session)
        click.echo(format_stamp_validation(result))
        if not result:
            any_failed = True

    if any_failed:
        raise SystemExit(2)
