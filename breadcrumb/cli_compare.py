"""CLI command for comparing two sessions."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.comparator import compare_sessions, format_compare


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="compare")
def compare_cmd():
    """Compare two sessions."""


@compare_cmd.command(name="run")
@click.argument("session_a")
@click.argument("session_b")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def run_compare(session_a: str, session_b: str, as_json: bool):
    """Compare SESSION_A and SESSION_B by their commands."""
    store = _get_store()
    a = store.load(session_a)
    if a is None:
        click.echo(f"Session not found: {session_a}", err=True)
        raise SystemExit(1)
    b = store.load(session_b)
    if b is None:
        click.echo(f"Session not found: {session_b}", err=True)
        raise SystemExit(1)

    result = compare_sessions(a, b)

    if as_json:
        import json
        click.echo(json.dumps({
            "session_a": result.session_a,
            "session_b": result.session_b,
            "similarity_pct": result.similarity_pct,
            "common_commands": result.common_commands,
            "only_in_a": result.only_in_a,
            "only_in_b": result.only_in_b,
        }, indent=2))
    else:
        click.echo(format_compare(result))
