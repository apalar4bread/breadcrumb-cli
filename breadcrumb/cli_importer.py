"""CLI commands for importing shell history into a session."""

import click
from pathlib import Path

from breadcrumb.store import SessionStore
from breadcrumb.importer import import_from_history_file, import_from_lines, import_summary
from breadcrumb.session import Session


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("import")
def import_cmd():
    """Import steps from shell history or plain text files."""


@import_cmd.command("history")
@click.argument("session_name")
@click.argument("file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option("--limit", "-n", default=None, type=int, help="Max number of commands to import.")
@click.option("--skip-duplicates", is_flag=True, default=False, help="Skip duplicate commands.")
def from_history(session_name: str, file: Path, limit: int, skip_duplicates: bool):
    """Import commands from a bash/zsh history file into SESSION_NAME."""
    store = _get_store()

    existing = store.find_by_name(session_name)
    if existing:
        session = existing
        click.echo(f"Appending to existing session '{session_name}'.")
    else:
        session = Session(name=session_name)
        click.echo(f"Creating new session '{session_name}'.")

    try:
        updated, count = import_from_history_file(
            session,
            file,
            limit=limit,
            skip_duplicates=skip_duplicates,
        )
    except Exception as e:
        raise click.ClickException(str(e))

    store.save(updated)
    summary = import_summary(count)
    click.echo(summary)


@import_cmd.command("lines")
@click.argument("session_name")
@click.argument("file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option("--limit", "-n", default=None, type=int, help="Max number of lines to import.")
@click.option("--skip-duplicates", is_flag=True, default=False, help="Skip duplicate commands.")
@click.option("--note", default="", help="Optional note to attach to every imported step.")
def from_lines(session_name: str, file: Path, limit: int, skip_duplicates: bool, note: str):
    """Import each line of FILE as a step into SESSION_NAME."""
    store = _get_store()

    existing = store.find_by_name(session_name)
    if existing:
        session = existing
        click.echo(f"Appending to existing session '{session_name}'.")
    else:
        session = Session(name=session_name)
        click.echo(f"Creating new session '{session_name}'.")

    try:
        raw_lines = file.read_text(encoding="utf-8").splitlines()
        updated, count = import_from_lines(
            session,
            raw_lines,
            limit=limit,
            skip_duplicates=skip_duplicates,
            note=note or None,
        )
    except Exception as e:
        raise click.ClickException(str(e))

    store.save(updated)
    summary = import_summary(count)
    click.echo(summary)


@import_cmd.command("preview")
@click.argument("file", type=click.Path(exists=True, readable=True, path_type=Path))
@click.option("--limit", "-n", default=10, show_default=True, help="Number of lines to preview.")
@click.option("--history", "is_history", is_flag=True, default=False, help="Parse as bash history format.")
def preview(file: Path, limit: int, is_history: bool):
    """Preview commands that would be imported from FILE."""
    from breadcrumb.importer import _strip_bash_history_number

    lines = file.read_text(encoding="utf-8").splitlines()
    shown = 0
    click.echo(f"Preview of '{file.name}' (first {limit} importable lines):")
    click.echo("-" * 40)
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if is_history:
            stripped = _strip_bash_history_number(stripped)
        if not stripped:
            continue
        click.echo(f"  {shown + 1:>3}. {stripped}")
        shown += 1
        if shown >= limit:
            break
    click.echo("-" * 40)
    click.echo(f"Showing {shown} line(s).")
