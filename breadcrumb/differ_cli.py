"""CLI commands for diffing two sessions side by side."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.differ import diff_sessions, format_diff, sessions_are_identical


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="diff")
def diff_cmd():
    """Compare two sessions and show what changed."""


@diff_cmd.command(name="show")
@click.argument("session_a")
@click.argument("session_b")
@click.option("--color/--no-color", default=True, help="Enable or disable colored output.")
def show_diff(session_a: str, session_b: str, color: bool):
    """Show a step-by-step diff between SESSION_A and SESSION_B."""
    store = _get_store()

    sess_a = store.load(session_a)
    if sess_a is None:
        click.echo(f"Session not found: {session_a}", err=True)
        raise SystemExit(1)

    sess_b = store.load(session_b)
    if sess_b is None:
        click.echo(f"Session not found: {session_b}", err=True)
        raise SystemExit(1)

    if sessions_are_identical(sess_a, sess_b):
        click.echo("Sessions are identical — no differences found.")
        return

    result = diff_sessions(sess_a, sess_b)
    output = format_diff(result, use_color=color)
    click.echo(output)


@diff_cmd.command(name="check")
@click.argument("session_a")
@click.argument("session_b")
def check_identical(session_a: str, session_b: str):
    """Exit with code 0 if sessions are identical, 1 if they differ."""
    store = _get_store()

    sess_a = store.load(session_a)
    if sess_a is None:
        click.echo(f"Session not found: {session_a}", err=True)
        raise SystemExit(2)

    sess_b = store.load(session_b)
    if sess_b is None:
        click.echo(f"Session not found: {session_b}", err=True)
        raise SystemExit(2)

    if sessions_are_identical(sess_a, sess_b):
        click.echo("identical")
        raise SystemExit(0)
    else:
        click.echo("different")
        raise SystemExit(1)
