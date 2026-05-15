"""CLI commands for importing tags into sessions."""

from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.tagger_importer import (
    TagImportError,
    import_tags_from_list,
    import_tags_from_text,
)


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("tag-import")
def tag_import_cmd():
    """Import tags into sessions from various sources."""


@tag_import_cmd.command("add")
@click.argument("session_name")
@click.argument("tags", nargs=-1, required=True)
def add_tags(session_name: str, tags):
    """Add one or more tags to SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = import_tags_from_list(session, list(tags))
        store.save(session)
        click.echo(result.summary())
    except TagImportError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@tag_import_cmd.command("from-text")
@click.argument("session_name")
@click.argument("text")
def from_text(session_name: str, text: str):
    """Import comma- or newline-separated tags from TEXT into SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = import_tags_from_text(session, text)
        store.save(session)
        click.echo(result.summary())
    except TagImportError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
