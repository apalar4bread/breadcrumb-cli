import click
from breadcrumb.store import SessionStore
from breadcrumb.pinboard import collect_pinned, format_pinboard, PinboardError

_DEFAULT_DIR = click.get_app_dir("breadcrumb")


def _get_store(store_dir):
    return SessionStore(store_dir)


@click.group("pinboard")
def pinboard_cmd():
    """View and manage pinned steps across sessions."""


@pinboard_cmd.command("show")
@click.option("--store-dir", default=_DEFAULT_DIR, hidden=True)
def show_pinboard(store_dir):
    """Show all pinned steps across all sessions."""
    store = _get_store(store_dir)
    sessions = [store.load(name) for name in store.list()]
    try:
        entries = collect_pinned(sessions)
    except PinboardError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if not entries:
        click.echo("No pinned steps found.")
        return

    click.echo(format_pinboard(entries))


@pinboard_cmd.command("count")
@click.option("--store-dir", default=_DEFAULT_DIR, hidden=True)
def count_pinned(store_dir):
    """Count total pinned steps across all sessions."""
    store = _get_store(store_dir)
    sessions = [store.load(name) for name in store.list()]
    entries = collect_pinned(sessions)
    click.echo(f"Pinned steps: {len(entries)}")
