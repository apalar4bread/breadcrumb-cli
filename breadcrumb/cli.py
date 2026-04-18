import click
from breadcrumb.store import SessionStore
from breadcrumb.session import Session
from breadcrumb.exporter import export_to_script, write_script
from breadcrumb.formatter import format_session, format_session_list
from breadcrumb.replayer import replay_session
from breadcrumb.cli_diff import diff_cmd
from breadcrumb.cli_validate import validate_cmd
from breadcrumb.cli_duplicates import dupes_cmd

DEFAULT_STORE = ".breadcrumb"


@click.group()
@click.option("--store", default=DEFAULT_STORE, envvar="BREADCRUMB_STORE",
              help="Path to session store directory.")
@click.pass_context
def cli(ctx, store):
    ctx.ensure_object(dict)
    ctx.obj["store"] = SessionStore(store)


@cli.command()
@click.argument("name")
@click.pass_context
def new(ctx, name):
    """Create a new session."""
    store: SessionStore = ctx.obj["store"]
    if store.load(name):
        click.echo(f"Session '{name}' already exists.", err=True)
        ctx.exit(1)
        return
    session = Session(name=name)
    store.save(session)
    click.echo(f"Created session '{name}'.")


@cli.command()
@click.argument("session_name")
@click.argument("command")
@click.option("--note", default=None)
@click.option("--tag", default=None)
@click.pass_context
def add(ctx, session_name, command, note, tag):
    """Add a step to a session."""
    store: SessionStore = ctx.obj["store"]
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        ctx.exit(1)
        return
    meta = {}
    if note:
        meta["note"] = note
    if tag:
        meta["tag"] = tag
    session.add_step(command, metadata=meta if meta else None)
    store.save(session)
    click.echo(f"Added step to '{session_name}'.")


@cli.command("list")
@click.pass_context
def list_sessions(ctx):
    """List all sessions."""
    store: SessionStore = ctx.obj["store"]
    sessions = store.list_sessions()
    if not sessions:
        click.echo("No sessions found.")
        return
    click.echo(format_session_list(sessions))


@cli.command()
@click.argument("session_name")
@click.option("--output", "-o", default=None)
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def export(ctx, session_name, output, verbose):
    """Export a session as a shell script."""
    store: SessionStore = ctx.obj["store"]
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        ctx.exit(1)
        return
    script = export_to_script(session, verbose=verbose)
    if output:
        write_script(script, output)
        click.echo(f"Script written to '{output}'.")
    else:
        click.echo(script)


@cli.command()
@click.argument("session_name")
@click.option("--dry-run", is_flag=True)
@click.pass_context
def replay(ctx, session_name, dry_run):
    """Replay a session's steps."""
    store: SessionStore = ctx.obj["store"]
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        ctx.exit(1)
        return
    replay_session(session, dry_run=dry_run)


cli.add_command(diff_cmd, "diff")
cli.add_command(validate_cmd, "validate")
cli.add_command(dupes_cmd, "dupes")
