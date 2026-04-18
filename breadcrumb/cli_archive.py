"""CLI commands for archiving and restoring sessions."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.archiver import export_archive, import_archive, archive_summary, ArchiveError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("archive")
def archive_cmd():
    """Archive and restore sessions."""


@archive_cmd.command("export")
@click.argument("output")
@click.option("--session", "session_ids", multiple=True, help="Session IDs to include (default: all).")
def export_cmd(output, session_ids):
    """Export sessions to a JSON archive file."""
    store = _get_store()
    if session_ids:
        sessions = []
        for sid in session_ids:
            s = store.load(sid)
            if s is None:
                click.echo(f"Session not found: {sid}", err=True)
                raise SystemExit(1)
            sessions.append(s)
    else:
        sessions = [store.load(sid) for sid in store.list_sessions()]

    try:
        path = export_archive(sessions, output)
        click.echo(f"Exported {len(sessions)} session(s) to {path}")
    except ArchiveError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@archive_cmd.command("import")
@click.argument("input")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite existing sessions.")
def import_cmd(input, overwrite):
    """Import sessions from a JSON archive file."""
    store = _get_store()
    try:
        sessions = import_archive(input)
    except ArchiveError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    imported = 0
    for s in sessions:
        existing = store.load(s.id)
        if existing and not overwrite:
            click.echo(f"Skipping existing session: {s.id} ({s.name})")
            continue
        store.save(s)
        imported += 1

    click.echo(f"Imported {imported} session(s) from {input}")


@archive_cmd.command("info")
@click.argument("input")
def info_cmd(input):
    """Show summary info about an archive file."""
    try:
        info = archive_summary(input)
    except ArchiveError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    click.echo(f"Archive : {info['path']}")
    click.echo(f"Sessions: {info['session_count']}")
    click.echo(f"Steps   : {info['total_steps']}")
    for name in info["session_names"]:
        click.echo(f"  - {name}")
