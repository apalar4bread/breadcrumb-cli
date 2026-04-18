"""CLI commands for duplicate detection and removal."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.duplicates import find_duplicate_steps, remove_duplicate_steps


@click.group("dupes")
def dupes_cmd():
    """Find and remove duplicate steps in a session."""
    pass


@dupes_cmd.command("find")
@click.argument("session_name")
@click.pass_context
def find_dupes(ctx, session_name):
    """List duplicate steps in SESSION_NAME."""
    store: SessionStore = ctx.obj["store"]
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        ctx.exit(1)
        return

    dupes = find_duplicate_steps(session)
    if not dupes:
        click.echo("No duplicate steps found.")
        return

    click.echo(f"Found {len(dupes)} duplicate pair(s):")
    for a, b in dupes:
        cmd = session.steps[a].command
        click.echo(f"  Step {a} and Step {b}: '{cmd}'")


@dupes_cmd.command("remove")
@click.argument("session_name")
@click.option("--keep", default="first", type=click.Choice(["first", "last"]),
              show_default=True, help="Which occurrence to keep.")
@click.option("--dry-run", is_flag=True, help="Preview without saving.")
@click.pass_context
def remove_dupes(ctx, session_name, keep, dry_run):
    """Remove duplicate steps from SESSION_NAME."""
    store: SessionStore = ctx.obj["store"]
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        ctx.exit(1)
        return

    before = len(session.steps)
    cleaned = remove_duplicate_steps(session, keep=keep)
    after = len(cleaned.steps)
    removed = before - after

    if dry_run:
        click.echo(f"[dry-run] Would remove {removed} duplicate step(s).")
        return

    store.save(cleaned)
    click.echo(f"Removed {removed} duplicate step(s) from '{session_name}'.")
