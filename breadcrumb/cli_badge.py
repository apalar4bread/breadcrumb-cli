"""CLI commands for the badge feature."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.badge import award_badges, format_badge_result


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("badge")
def badge_cmd():
    """Award and display session badges."""


@badge_cmd.command("show")
@click.argument("session_name")
def show_badges(session_name: str):
    """Show badges earned by a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    result = award_badges(session)
    click.echo(format_badge_result(result))


@badge_cmd.command("summary")
@click.argument("session_name")
def badge_summary(session_name: str):
    """Print a one-line badge summary for a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    result = award_badges(session)
    click.echo(result.summary())


@badge_cmd.command("all")
def all_badges():
    """Show badge counts for every stored session."""
    store = _get_store()
    names = store.list_sessions()
    if not names:
        click.echo("No sessions found.")
        return
    for name in sorted(names):
        session = store.load(name)
        if session is None:
            continue
        result = award_badges(session)
        click.echo(f"{name}: {result.count} badge(s)")
