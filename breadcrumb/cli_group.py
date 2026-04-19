"""CLI commands for grouping session steps."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.grouper import group_steps, GroupError, VALID_KEYS


def _get_store():
    return SessionStore()


@click.group(name="group")
def group_cmd():
    """Group steps within a session by a given attribute."""


@group_cmd.command(name="by")
@click.argument("session_name")
@click.argument("key", type=click.Choice(sorted(VALID_KEYS)))
@click.option("--counts", is_flag=True, help="Show only group counts.")
def by_key(session_name, key, counts):
    """Group steps in SESSION_NAME by KEY."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    try:
        groups = group_steps(session, key)
    except GroupError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)

    if not groups:
        click.echo("No steps to group.")
        return

    for group_name, steps in sorted(groups.items()):
        if counts:
            click.echo(f"{group_name}: {len(steps)} step(s)")
        else:
            click.echo(f"\n[{group_name}]")
            for i, step in enumerate(steps, 1):
                note = f" # {step.note}" if step.note else ""
                click.echo(f"  {i}. {step.command}{note}")
