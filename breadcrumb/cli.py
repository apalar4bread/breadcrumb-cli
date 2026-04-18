"""CLI entry point for breadcrumb."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.exporter import export_to_script, write_script
from breadcrumb.formatter import format_session, format_session_list
from breadcrumb.tagger import add_tag, remove_tag, list_tags, find_by_tag

store = SessionStore()


@click.group()
def cli():
    """breadcrumb — track and replay terminal sessions."""


@cli.command()
@click.argument("name")
def new(name):
    """Create a new session."""
    from breadcrumb.session import Session
    session = Session(name=name)
    store.save(session)
    click.echo(f"Created session: {name}")


@cli.command()
@click.argument("session_name")
@click.argument("command")
@click.option("--desc", default="", help="Step description")
def add(session_name, command, desc):
    """Add a step to a session."""
    session = store.load(session_name)
    if not session:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    session.add_step(command, description=desc)
    store.save(session)
    click.echo(f"Added step to '{session_name}': {command}")


@cli.command(name="list")
def list_sessions():
    """List all sessions."""
    sessions = [store.load(n) for n in store.list_sessions()]
    sessions = [s for s in sessions if s]
    click.echo(format_session_list(sessions))


@cli.command()
@click.argument("session_name")
@click.option("--output", "-o", default=None, help="Output file path")
def export(session_name, output):
    """Export a session as a shell script."""
    session = store.load(session_name)
    if not session:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    script = export_to_script(session)
    if output:
        write_script(script, output)
        click.echo(f"Script written to {output}")
    else:
        click.echo(script)


@cli.command()
@click.argument("session_name")
@click.argument("tag")
def tag(session_name, tag):
    """Add a tag to a session."""
    session = store.load(session_name)
    if not session:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    add_tag(session, tag)
    store.save(session)
    click.echo(f"Tagged '{session_name}' with '{tag.strip().lower()}'")


@cli.command()
@click.argument("session_name")
@click.argument("tag")
def untag(session_name, tag):
    """Remove a tag from a session."""
    session = store.load(session_name)
    if not session:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    remove_tag(session, tag)
    store.save(session)
    click.echo(f"Removed tag '{tag.strip().lower()}' from '{session_name}'")


@cli.command(name="find-tag")
@click.argument("tag")
def find_tag(tag):
    """Find sessions by tag."""
    results = find_by_tag(store, tag)
    if not results:
        click.echo(f"No sessions found with tag '{tag}'.")
    else:
        click.echo(format_session_list(results))


if __name__ == "__main__":
    cli()
