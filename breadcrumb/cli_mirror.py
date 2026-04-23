"""CLI commands for the mirror feature."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.mirror import MirrorError, MirrorResult, mirror_session, format_mirror_result


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("mirror")
def mirror_cmd():
    """Mirror (reverse/copy) a session."""


@mirror_cmd.command("run")
@click.argument("session_id")
@click.option("--name", default=None, help="Name for the mirrored session.")
@click.option("--no-reverse", is_flag=True, default=False, help="Copy without reversing step order.")
@click.option("--save", is_flag=True, default=False, help="Persist the mirrored session to the store.")
def run_mirror(session_id: str, name: str, no_reverse: bool, save: bool):
    """Create a mirrored copy of SESSION_ID."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        mirrored = mirror_session(session, name=name, reverse=not no_reverse)
    except MirrorError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    result = MirrorResult(
        original_name=session.name,
        mirrored_name=mirrored.name,
        step_count=len(mirrored.steps),
        reversed=not no_reverse,
    )
    click.echo(format_mirror_result(result))

    if save:
        store.save(mirrored)
        click.echo(f"Saved as '{mirrored.id}'.")
    else:
        click.echo("(use --save to persist the mirrored session)")
