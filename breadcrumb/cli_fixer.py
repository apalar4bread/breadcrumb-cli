"""cli_fixer.py — CLI commands for the fixer module."""

import click

from breadcrumb.store import SessionStore
from breadcrumb.fixer import fix_session, FixError


def _get_store(path: str) -> SessionStore:
    return SessionStore(base_dir=path)


@click.group("fix")
def fix_cmd():
    """Automatically fix common issues in a session."""


@fix_cmd.command("run")
@click.argument("session_id")
@click.option("--store", default=".breadcrumb", help="Store directory.")
@click.option("--no-strip", is_flag=True, default=False, help="Skip whitespace stripping.")
@click.option("--no-remove-empty", is_flag=True, default=False, help="Keep empty commands.")
@click.option("--no-dedupe-notes", is_flag=True, default=False, help="Skip note deduplication.")
@click.option("--dry-run", is_flag=True, default=False, help="Preview fixes without saving.")
def run_fix(session_id, store, no_strip, no_remove_empty, no_dedupe_notes, dry_run):
    """Run automatic fixes on SESSION_ID."""
    s = _get_store(store)
    session = s.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = fix_session(
            session,
            strip_whitespace=not no_strip,
            remove_empty=not no_remove_empty,
            dedupe_notes=not no_dedupe_notes,
        )
    except FixError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    click.echo(result.summary())

    if dry_run:
        click.echo("(dry-run: changes not saved)")
    else:
        s.save(result.session)
        click.echo(f"Session '{session_id}' updated.")
