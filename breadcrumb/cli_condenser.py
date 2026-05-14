"""cli_condenser.py — CLI commands for the condenser module."""
from __future__ import annotations

import click

from breadcrumb.condenser import condense_session, CondenserError
from breadcrumb.store import SessionStore


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("condense")
def condense_cmd() -> None:
    """Condense a session to a smaller number of steps."""


@condense_cmd.command("run")
@click.argument("session_id")
@click.option("--max", "max_steps", required=True, type=int, help="Maximum steps to keep.")
@click.option(
    "--strategy",
    default="first",
    show_default=True,
    type=click.Choice(["first", "last", "spread"], case_sensitive=False),
    help="Selection strategy.",
)
@click.option("--name", default=None, help="Name for the condensed session.")
@click.option("--save", is_flag=True, default=False, help="Persist the condensed session.")
def run_condense(
    session_id: str,
    max_steps: int,
    strategy: str,
    name: str | None,
    save: bool,
) -> None:
    """Condense SESSION_ID to at most MAX steps."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = condense_session(session, max_steps=max_steps, name=name, strategy=strategy)
    except CondenserError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(result.summary())
    for i, step in enumerate(result.session.steps, 1):
        note_part = f"  # {step.note}" if step.note else ""
        click.echo(f"  [{i}] {step.command}{note_part}")

    if save:
        store.save(result.session)
        click.echo(f"Saved condensed session '{result.session.name}'.")
