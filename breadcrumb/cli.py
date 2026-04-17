"""CLI entry point for breadcrumb-cli using Click."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.session import Session
from breadcrumb.exporter import export_to_script, write_script

store = SessionStore()


@click.group()
def cli():
    """breadcrumb - track and replay terminal session steps."""
    pass


@cli.command()
@click.argument("name")
def new(name):
    """Start a new session with the given NAME."""
    session = Session(name=name)
    store.save(session)
    click.echo(f"Created session '{name}' ({session.id})")


@cli.command()
@click.argument("session_id")
@click.argument("command")
@click.option("--note", default="", help="Optional note for this step.")
def add(session_id, command, note):
    """Add a COMMAND step to SESSION_ID."""
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    metadata = {"note": note} if note else {}
    session.add_step(command=command, metadata=metadata)
    store.save(session)
    click.echo(f"Added step: {command}")


@cli.command(name="list")
def list_sessions():
    """List all saved sessions."""
    sessions = store.list_sessions()
    if not sessions:
        click.echo("No sessions found.")
        return
    for s in sessions:
        click.echo(f"{s['id']}  {s['name']}  ({s['step_count']} steps)")


@cli.command()
@click.argument("session_id")
@click.option("--output", "-o", default=None, help="Output file path.")
def export(session_id, output):
    """Export SESSION_ID as a shell script."""
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    script = export_to_script(session)
    if output:
        write_script(script, output)
        click.echo(f"Script written to {output}")
    else:
        click.echo(script)


@cli.command()
@click.argument("session_id")
def delete(session_id):
    """Delete a session by SESSION_ID."""
    deleted = store.delete(session_id)
    if deleted:
        click.echo(f"Deleted session {session_id}")
    else:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
