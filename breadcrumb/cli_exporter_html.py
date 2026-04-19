"""CLI command: breadcrumb export-html <session_id> <output.html>"""
from __future__ import annotations

import click
from breadcrumb.store import SessionStore
from breadcrumb.exporter_html import write_html


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("export-html")
def html_cmd():
    """Export a session to an HTML file."""


@html_cmd.command("run")
@click.argument("session_id")
@click.argument("output")
def run_export(session_id: str, output: str):
    """Export SESSION_ID to OUTPUT (.html)."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        path = write_html(session, output)
        click.echo(f"Exported '{session.name}' to {path}")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
