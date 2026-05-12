import click
from breadcrumb.store import SessionStore
from breadcrumb.tagger import add_tag, remove_tag, list_tags, find_by_tag


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("tag")
def tag_cmd():
    """Manage tags on sessions."""


@tag_cmd.command("add")
@click.argument("session_id")
@click.argument("tag")
def add_cmd(session_id: str, tag: str):
    """Add a tag to a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    add_tag(session, tag)
    store.save(session)
    click.echo(f"Tag '{tag.lower()}' added to session '{session_id}'.")


@tag_cmd.command("remove")
@click.argument("session_id")
@click.argument("tag")
def remove_cmd(session_id: str, tag: str):
    """Remove a tag from a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    remove_tag(session, tag)
    store.save(session)
    click.echo(f"Tag '{tag.lower()}' removed from session '{session_id}'.")


@tag_cmd.command("list")
@click.argument("session_id")
def list_cmd(session_id: str):
    """List all tags on a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    tags = list_tags(session)
    if not tags:
        click.echo("No tags.")
    else:
        for t in tags:
            click.echo(t)


@tag_cmd.command("find")
@click.argument("tag")
def find_cmd(tag: str):
    """Find sessions with a given tag."""
    store = _get_store()
    sessions = store.list_sessions()
    all_sessions = [store.load(s) for s in sessions]
    matches = find_by_tag(all_sessions, tag)
    if not matches:
        click.echo("No sessions found with that tag.")
    else:
        for s in matches:
            click.echo(f"{s.id}  {s.name}")
