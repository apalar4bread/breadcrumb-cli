"""CLI commands for bookmarking session steps."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.bookmarker import bookmark_step, unbookmark_step, list_bookmarked, BookmarkError


def _get_store():
    return SessionStore()


@click.group("bookmark")
def bookmark_cmd():
    """Manage step bookmarks."""


@bookmark_cmd.command("add")
@click.argument("session_name")
@click.argument("step_index", type=int)
def add_bookmark(session_name, step_index):
    """Bookmark a step by index."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        bookmark_step(session, step_index)
        store.save(session)
        click.echo(f"Bookmarked step {step_index} in '{session_name}'.")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_cmd.command("remove")
@click.argument("session_name")
@click.argument("step_index", type=int)
def remove_bookmark(session_name, step_index):
    """Remove a bookmark from a step."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        unbookmark_step(session, step_index)
        store.save(session)
        click.echo(f"Removed bookmark from step {step_index} in '{session_name}'.")
    except BookmarkError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@bookmark_cmd.command("list")
@click.argument("session_name")
def list_bookmarks(session_name):
    """List all bookmarked steps in a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    bookmarks = list_bookmarked(session)
    if not bookmarks:
        click.echo("No bookmarked steps.")
    else:
        for idx, step in bookmarks:
            note = f" # {step.note}" if step.note else ""
            click.echo(f"  [{idx}] {step.command}{note}")
