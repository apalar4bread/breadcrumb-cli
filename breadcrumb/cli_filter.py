"""CLI commands for filtering session steps."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.filterer import filter_by_command, filter_by_note, filter_by_metadata_key, FilterError
from breadcrumb.formatter import format_step


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="filter")
def filter_cmd():
    """Filter steps within a session."""


@filter_cmd.command(name="command")
@click.argument("session_name")
@click.argument("pattern")
@click.option("--case-sensitive", is_flag=True, default=False)
def by_command(session_name, pattern, case_sensitive):
    """Filter steps by command pattern."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        steps = filter_by_command(session, pattern, case_sensitive=case_sensitive)
    except FilterError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if not steps:
        click.echo("No matching steps found.")
        return
    for i, step in enumerate(steps):
        click.echo(format_step(i, step))


@filter_cmd.command(name="note")
@click.argument("session_name")
@click.argument("pattern")
@click.option("--case-sensitive", is_flag=True, default=False)
def by_note(session_name, pattern, case_sensitive):
    """Filter steps by note pattern."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        steps = filter_by_note(session, pattern, case_sensitive=case_sensitive)
    except FilterError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if not steps:
        click.echo("No matching steps found.")
        return
    for i, step in enumerate(steps):
        click.echo(format_step(i, step))


@filter_cmd.command(name="meta")
@click.argument("session_name")
@click.argument("key")
def by_meta(session_name, key):
    """Filter steps that have a specific metadata key."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        steps = filter_by_metadata_key(session, key)
    except FilterError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    if not steps:
        click.echo("No matching steps found.")
        return
    for i, step in enumerate(steps):
        click.echo(format_step(i, step))
