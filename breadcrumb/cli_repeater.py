"""CLI commands for the repeater feature."""

from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.repeater import RepeatError, mark_repeat, clear_repeat, expand_repeats


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("repeat")
def repeat_cmd():
    """Mark steps for repetition and expand them."""


@repeat_cmd.command("mark")
@click.argument("session_name")
@click.argument("step_index", type=int)
@click.option("--times", "-t", default=2, show_default=True, help="How many times to repeat")
def mark_cmd(session_name: str, step_index: int, times: int):
    """Mark a step to be repeated TIMES times."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        raise click.ClickException(f"Session '{session_name}' not found")
    try:
        step = mark_repeat(session, step_index, times=times)
        store.save(session)
        click.echo(f"Marked step {step_index} ('{step.command}') to repeat {times}x.")
    except RepeatError as e:
        raise click.ClickException(str(e))


@repeat_cmd.command("clear")
@click.argument("session_name")
@click.argument("step_index", type=int)
def clear_cmd(session_name: str, step_index: int):
    """Remove repeat marker from a step."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        raise click.ClickException(f"Session '{session_name}' not found")
    try:
        clear_repeat(session, step_index)
        store.save(session)
        click.echo(f"Cleared repeat marker from step {step_index}.")
    except RepeatError as e:
        raise click.ClickException(str(e))


@repeat_cmd.command("expand")
@click.argument("session_name")
@click.option("--name", "-n", default=None, help="Name for the expanded session")
@click.option("--save", "save_result", is_flag=True, default=False, help="Save expanded session")
def expand_cmd(session_name: str, name: str | None, save_result: bool):
    """Expand repeated steps into a new session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        raise click.ClickException(f"Session '{session_name}' not found")
    try:
        result = expand_repeats(session, name=name)
        click.echo(result.summary)
        if save_result:
            store.save(result.new_session)
            click.echo(f"Saved as '{result.new_session.name}'.")
        else:
            for i, step in enumerate(result.new_session.steps):
                click.echo(f"  [{i}] {step.command}")
    except RepeatError as e:
        raise click.ClickException(str(e))
