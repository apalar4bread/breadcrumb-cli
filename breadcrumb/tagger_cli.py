import click
from breadcrumb.store import SessionStore
from breadcrumb.tagger import add_tag, remove_tag, list_tags, find_by_tag


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="tag")
def tag_cmd():
    """Manage tags on sessions."""


@tag_cmd.command(name="add")
@click.argument("session_name")
@click.argument("tag")
def add_cmd(session_name: str, tag: str):
    """Add a tag to a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    add_tag(session, tag)
    store.save(session)
    click.echo(f"Tag '{tag.lower()}' added to '{session_name}'.")


@tag_cmd.command(name="remove")
@click.argument("session_name")
@click.argument("tag")
def remove_cmd(session_name: str, tag: str):
    """Remove a tag from a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    remove_tag(session, tag)
    store.save(session)
    click.echo(f"Tag '{tag.lower()}' removed from '{session_name}'.")


@tag_cmd.command(name="list")
@click.argument("session_name")
def list_cmd(session_name: str):
    """List all tags on a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    tags = list_tags(session)
    if not tags:
        click.echo("No tags.")
    else:
        for t in tags:
            click.echo(f"  {t}")


@tag_cmd.command(name="find")
@click.argument("tag")
def find_cmd(tag: str):
    """Find all sessions with a given tag."""
    store = _get_store()
    sessions = store.list_sessions()
    loaded = [store.load(n) for n in sessions]
    loaded = [s for s in loaded if s is not None]
    matches = find_by_tag(loaded, tag)
    if not matches:
        click.echo(f"No sessions found with tag '{tag}'.")
    else:
        for s in matches:
            click.echo(f"  {s.name}")
