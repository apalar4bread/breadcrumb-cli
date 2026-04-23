"""CLI commands for injecting steps into a session."""

import click

from breadcrumb.store import SessionStore
from breadcrumb.injector import InjectError, inject_step, inject_after, format_inject_result


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("inject")
def inject_cmd():
    """Insert steps into a session at a specific position."""


@inject_cmd.command("at")
@click.argument("session_name")
@click.argument("position", type=int)
@click.argument("command")
@click.option("--note", "-n", default=None, help="Optional note for the step.")
@click.option("--meta", "-m", multiple=True, metavar="KEY=VALUE", help="Metadata key=value pairs.")
def at_position(session_name, position, command, note, meta):
    """Insert COMMAND at POSITION (0-based) in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    metadata = {}
    for item in meta:
        if "=" in item:
            k, v = item.split("=", 1)
            metadata[k.strip()] = v.strip()

    try:
        result = inject_step(session, position, command, note=note, metadata=metadata)
    except InjectError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    store.save(session)
    click.echo(format_inject_result(result))


@inject_cmd.command("after")
@click.argument("session_name")
@click.argument("position", type=int)
@click.argument("command")
@click.option("--note", "-n", default=None, help="Optional note for the step.")
def after_position(session_name, position, command, note):
    """Insert COMMAND after POSITION in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = inject_after(session, position, command, note=note)
    except InjectError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    store.save(session)
    click.echo(format_inject_result(result))
