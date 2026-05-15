"""CLI commands for exporting tag data from sessions."""

from __future__ import annotations

import json

import click

from breadcrumb.store import SessionStore
from breadcrumb.tagger_exporter import (
    export_tags_flat,
    format_tags_text,
    all_unique_tags,
)


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("tag-export")
def tag_export_cmd():
    """Export tag information from sessions."""


@tag_export_cmd.command("text")
def show_text():
    """Print all session tags as plain text."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    click.echo(format_tags_text(sessions))


@tag_export_cmd.command("json")
def show_json():
    """Print all session tags as JSON."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    rows = export_tags_flat(sessions)
    click.echo(json.dumps(rows, indent=2))


@tag_export_cmd.command("unique")
def show_unique():
    """Print all unique tags across all sessions."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    tags = all_unique_tags(sessions)
    if not tags:
        click.echo("No tags found.")
    else:
        for tag in tags:
            click.echo(tag)
