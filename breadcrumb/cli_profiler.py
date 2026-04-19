"""CLI command for profiling a session."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.profiler import profile_session, format_profile


def _get_store(store_path):
    return SessionStore(store_path)


@click.group(name="profile")
def profile_cmd():
    """Profile a session's command patterns and timing."""


@profile_cmd.command(name="show")
@click.argument("session_id")
@click.option("--store", default="~/.breadcrumb", show_default=True, help="Store path.")
def show_profile(session_id, store):
    """Show a profile report for SESSION_ID."""
    st = _get_store(store)
    session = st.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    result = profile_session(session)
    click.echo(format_profile(result))


@profile_cmd.command(name="top")
@click.option("--store", default="~/.breadcrumb", show_default=True, help="Store path.")
@click.option("--limit", default=5, show_default=True, help="Number of sessions to show.")
def top_sessions(store, limit):
    """Show sessions ranked by step count."""
    st = _get_store(store)
    sessions = st.list_all()
    if not sessions:
        click.echo("No sessions found.")
        return
    profiles = [(s, profile_session(s)) for s in sessions]
    profiles.sort(key=lambda x: x[1].total_steps, reverse=True)
    for session, r in profiles[:limit]:
        click.echo(f"{r.total_steps:>4} steps  {r.unique_commands:>3} unique  {session.name} ({session.id})")
