"""cli_tracer.py — CLI commands for tracing command lineage in a session."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.tracer import TracerError, trace_session, format_trace


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("trace")
def trace_cmd():
    """Trace command lineage within a session."""


@trace_cmd.command("show")
@click.argument("session_name")
@click.argument("keyword")
@click.option("--case-sensitive", is_flag=True, default=False, help="Enable case-sensitive matching.")
def show_trace(session_name: str, keyword: str, case_sensitive: bool):
    """Show steps in SESSION_NAME whose commands contain KEYWORD, linked by lineage."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = trace_session(session, keyword, case_sensitive=case_sensitive)
    except TracerError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(format_trace(result))


@trace_cmd.command("count")
@click.argument("session_name")
@click.argument("keyword")
@click.option("--case-sensitive", is_flag=True, default=False)
def count_trace(session_name: str, keyword: str, case_sensitive: bool):
    """Print the number of steps in SESSION_NAME matching KEYWORD."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = trace_session(session, keyword, case_sensitive=case_sensitive)
    except TracerError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(f"{result.length} matching step(s) in '{session_name}' for keyword '{keyword}'.")
