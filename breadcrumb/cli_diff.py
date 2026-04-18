"""CLI commands for diffing sessions."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.differ import diff_sessions, format_diff, sessions_are_identical


@click.command("diff")
@click.argument("session_a")
@click.argument("session_b")
@click.option("--only-changes", is_flag=True, help="Show only changed/added/removed steps.")
@click.pass_context
def diff_cmd(ctx, session_a: str, session_b: str, only_changes: bool):
    """Diff two sessions by name and display differences."""
    store: SessionStore = ctx.obj["store"]

    sa = store.load(session_a)
    if sa is None:
        click.echo(f"Session '{session_a}' not found.", err=True)
        raise SystemExit(1)

    sb = store.load(session_b)
    if sb is None:
        click.echo(f"Session '{session_b}' not found.", err=True)
        raise SystemExit(1)

    diffs = diff_sessions(sa, sb)

    if sessions_are_identical(diffs):
        click.echo("Sessions are identical.")
        return

    if only_changes:
        filtered = [d for d in diffs if d["status"] != "same"]
    else:
        filtered = diffs

    click.echo(f"Diff: {session_a}  →  {session_b}")
    click.echo(format_diff(filtered))
