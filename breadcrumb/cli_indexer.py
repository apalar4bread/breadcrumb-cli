"""CLI commands for the step indexer."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.indexer import build_index, query_index, format_index_entry


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("index")
def index_cmd():
    """Build and query a cross-session step index."""


@index_cmd.command("search")
@click.option("--command", "-c", default=None, help="Filter by command substring.")
@click.option("--note", "-n", default=None, help="Filter by note substring.")
@click.option("--session", "-s", default=None, help="Filter by session name.")
@click.option("--case-sensitive", is_flag=True, default=False)
def search(command, note, session, case_sensitive):
    """Search all steps across every session."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    if not sessions:
        click.echo("No sessions found.")
        return
    idx = build_index(sessions)
    results = query_index(
        idx,
        command=command,
        note=note,
        session_name=session,
        case_sensitive=case_sensitive,
    )
    if not results:
        click.echo("No matching steps found.")
        return
    click.echo(f"{len(results)} result(s):")
    for entry in results:
        click.echo(format_index_entry(entry))
        click.echo()


@index_cmd.command("stats")
def stats():
    """Show total indexed steps across all sessions."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    idx = build_index(sessions)
    click.echo(f"Sessions indexed : {len(sessions)}")
    click.echo(f"Total steps      : {idx.total}")
