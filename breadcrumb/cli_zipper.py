"""CLI commands for the zipper feature."""

from __future__ import annotations

import click

from breadcrumb.store import SessionStore
from breadcrumb.zipper import ZipError, format_zip_result, zip_sessions


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="zip")
def zip_cmd():
    """Interleave steps from two sessions."""


@zip_cmd.command(name="merge")
@click.argument("left_name")
@click.argument("right_name")
@click.option("--name", default=None, help="Name for the resulting session.")
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Require both sessions to have equal step counts.",
)
@click.option("--save", is_flag=True, default=False, help="Persist the zipped session.")
def run_zip(left_name: str, right_name: str, name: str | None, strict: bool, save: bool):
    """Interleave LEFT_NAME and RIGHT_NAME steps alternately."""
    store = _get_store()

    left = store.load(left_name)
    if left is None:
        raise click.ClickException(f"Session not found: {left_name}")

    right = store.load(right_name)
    if right is None:
        raise click.ClickException(f"Session not found: {right_name}")

    try:
        result = zip_sessions(left, right, name=name, strict=strict)
    except ZipError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(format_zip_result(result))

    if save:
        store.save(result.session)
        click.echo(f"Saved as '{result.session.name}'.")
