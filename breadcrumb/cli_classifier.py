"""CLI commands for step classification."""

from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.classifier import classify_session, ClassifyError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="classify")
def classify_cmd():
    """Classify steps in a session by command type."""


@classify_cmd.command(name="show")
@click.argument("session_id")
@click.option("--verbose", "-v", is_flag=True, help="Show step indices per category.")
def show_classify(session_id: str, verbose: bool):
    """Show classification breakdown for a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = classify_session(session)
    except ClassifyError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)

    click.echo(f"Session: {session.name}")
    click.echo(result.summary())

    if verbose:
        click.echo()
        for cat, indices in sorted(result.categories.items()):
            click.echo(f"  [{cat}]")
            for i in indices:
                step = session.steps[i]
                click.echo(f"    #{i}: {step.command}")
        if result.uncategorized:
            click.echo("  [other]")
            for i in result.uncategorized:
                step = session.steps[i]
                click.echo(f"    #{i}: {step.command}")


@classify_cmd.command(name="step")
@click.argument("session_id")
@click.argument("index", type=int)
def classify_one(session_id: str, index: int):
    """Show the category of a single step."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    if index < 0 or index >= len(session.steps):
        click.echo(f"Step index {index} out of range.", err=True)
        raise SystemExit(1)

    from breadcrumb.classifier import classify_step
    step = session.steps[index]
    category = classify_step(step)
    click.echo(f"Step #{index}: '{step.command}' -> {category}")
