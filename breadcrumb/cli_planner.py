"""CLI commands for the planner feature."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.planner import (
    PlanError,
    add_planned_step,
    list_planned,
    clear_planned,
    promote_planned,
)


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("plan")
def plan_cmd():
    """Manage planned (future) steps for a session."""


@plan_cmd.command("add")
@click.argument("session_id")
@click.argument("command")
@click.option("--note", default="", help="Optional note for the planned step.")
@click.option("--order", default=None, type=int, help="Explicit order index.")
def add_plan(session_id, command, note, order):
    """Add a planned step to a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        step = add_planned_step(session, command, note=note, order=order)
        store.save(session)
        click.echo(f"Planned step added (order={step.order}): {step.command}")
    except PlanError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@plan_cmd.command("list")
@click.argument("session_id")
def list_plan(session_id):
    """List all planned steps for a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    steps = list_planned(session)
    if not steps:
        click.echo("No planned steps.")
        return
    for ps in steps:
        note_part = f"  # {ps.note}" if ps.note else ""
        click.echo(f"[{ps.order}] {ps.command}{note_part}")


@plan_cmd.command("clear")
@click.argument("session_id")
def clear_plan(session_id):
    """Remove all planned steps from a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    removed = clear_planned(session)
    store.save(session)
    click.echo(f"Cleared {removed} planned step(s).")


@plan_cmd.command("promote")
@click.argument("session_id")
@click.argument("order", type=int)
def promote_plan(session_id, order):
    """Promote a planned step to a real step."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        step = promote_planned(session, order=order)
        store.save(session)
        click.echo(f"Promoted: {step.command}")
    except PlanError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
