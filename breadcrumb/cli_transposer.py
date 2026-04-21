"""CLI commands for transposing (swapping) steps in a session."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.transposer import TransposeError, transpose_steps, format_transpose_result


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("transpose")
def transpose_cmd():
    """Swap two steps within a session."""


@transpose_cmd.command("swap")
@click.argument("session_name")
@click.argument("index_a", type=int)
@click.argument("index_b", type=int)
@click.option("--dry-run", is_flag=True, help="Preview the swap without saving.")
def swap(session_name: str, index_a: int, index_b: int, dry_run: bool):
    """Swap steps INDEX_A and INDEX_B in SESSION_NAME."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = transpose_steps(session, index_a, index_b)
    except TransposeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(format_transpose_result(result))

    if dry_run:
        click.echo("(dry run — changes not saved)")
    else:
        store.save(session)
        click.echo("Session updated.")
