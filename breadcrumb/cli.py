import click
from breadcrumb.session import Session
from breadcrumb.store import SessionStore
from breadcrumb.exporter import export_to_script, write_script
from breadcrumb.replayer import replay_session

store = SessionStore()


@click.group()
def cli():
    """breadcrumb — track and replay terminal sessions."""
    pass


@cli.command()
@click.argument("name")
def new(name):
    """Create a new session."""
    session = Session(name=name)
    store.save(session)
    click.echo(f"Created session '{name}' ({session.id})")


@cli.command()
@click.argument("session_id")
@click.argument("command")
@click.option("--note", default=None, help="Optional note for this step.")
def add(session_id, command, note):
    """Add a step to a session."""
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise Systemmetadata = {"note": note} if note else {}
    session.add_step(command, metadata=metadata)
    store.save(session)
    click.echo(f"Added step: {command}")


@cli.command(name="list")
def list_sessions():
    """List all sessions."""
    sessions = store.list_sessions()
    if not sessions:
        click.echo("No sessions found.")
        return
    for s in sessions:
        click.echo(f"{s['id']}  {s['name']}  ({s['step_count']} steps)")


@cli.command()
@click.argument("session_id")
@click.option("--output", "-o", default=None, help="Output file path.")
def export(session_id, output):
    """Export a session as a shell script."""
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    script = export_to_script(session)
    if output:
        write_script(script, output)
        click.echo(f"Script written to {output}")
    else:
        click.echo(script)


@cli.command()
@click.argument("session_id")
@click.option("--dry-run", is_flag=True, default=False, help="Print commands without running them.")
@click.option("--delay", default=0.5, show_default=True, help="Seconds between steps.")
@click.option("--no-stop-on-error", is_flag=True, default=False, help="Continue even if a step fails.")
def replay(session_id, dry_run, delay, no_stop_on_error):
    """Replay all steps in a session."""
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    click.echo(f"Replaying session '{session.name}' ({len(session.steps)} steps)...")
    results = replay_session(
        session,
        dry_run=dry_run,
        delay=delay,
        stop_on_error=not no_stop_on_error,
    )
    failed = [r for r in results if r["returncode"] != 0]
    click.echo(f"Done. {len(results)} step(s) run, {len(failed)} failed.")


if __name__ == "__main__":
    cli()
