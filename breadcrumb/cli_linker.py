"""CLI commands for session linking."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.linker import (
    add_link,
    remove_link,
    list_links,
    format_links,
    LinkError,
)


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("link")
def link_cmd():
    """Manage links between sessions."""


@link_cmd.command("add")
@click.argument("session_name")
@click.argument("target_id")
@click.option("--type", "link_type", default="related", show_default=True,
              help="Link type: depends-on, follows, related, blocks")
@click.option("--note", default=None, help="Optional note for the link.")
def add_cmd(session_name: str, target_id: str, link_type: str, note: str):
    """Add a link from SESSION_NAME to TARGET_ID."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        link = add_link(session, target_id=target_id, link_type=link_type, note=note)
        store.save(session)
        click.echo(f"Linked [{link.link_type}] → {link.target_id}")
    except LinkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@link_cmd.command("remove")
@click.argument("session_name")
@click.argument("target_id")
@click.option("--type", "link_type", default="related", show_default=True)
def remove_cmd(session_name: str, target_id: str, link_type: str):
    """Remove a link from SESSION_NAME to TARGET_ID."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        remove_link(session, target_id=target_id, link_type=link_type)
        store.save(session)
        click.echo("Link removed.")
    except LinkError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@link_cmd.command("list")
@click.argument("session_name")
def list_cmd(session_name: str):
    """List all links for SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    links = list_links(session)
    click.echo(format_links(links))
