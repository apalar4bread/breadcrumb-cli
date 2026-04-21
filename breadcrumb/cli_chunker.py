"""CLI commands for chunking a session into smaller pieces."""

import click

from breadcrumb.store import SessionStore
from breadcrumb.chunker import ChunkError, chunk_session, chunk_to_sessions, format_chunk_summary


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="chunk")
def chunk_cmd():
    """Split a session into fixed-size chunks."""


@chunk_cmd.command(name="show")
@click.argument("session_name")
@click.option("--size", "-s", default=5, show_default=True, help="Steps per chunk")
def show_chunks(session_name: str, size: int):
    """Display a chunk breakdown for a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        chunks = chunk_session(session, size)
    except ChunkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
    click.echo(format_chunk_summary(chunks))


@chunk_cmd.command(name="split")
@click.argument("session_name")
@click.option("--size", "-s", default=5, show_default=True, help="Steps per chunk")
@click.option("--save", is_flag=True, default=False, help="Persist each chunk as a new session")
def split_chunks(session_name: str, size: int, save: bool):
    """Split a session and optionally save each chunk as a new session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        sessions = chunk_to_sessions(session, size)
    except ChunkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    for s in sessions:
        click.echo(f"  {s.name}  ({len(s.steps)} steps)")
        if save:
            store.save(s)

    if save:
        click.echo(f"Saved {len(sessions)} chunk session(s).")
    else:
        click.echo(f"(Use --save to persist chunks.)")
