import click
from breadcrumb.store import SessionStore
from breadcrumb.statistics import session_stats, command_frequency, average_steps_per_session


def _get_store():
    return SessionStore()


@click.group("stats")
def stats_cmd():
    """Session statistics commands."""


@stats_cmd.command("show")
@click.argument("session_name")
def show_stats(session_name):
    """Show statistics for a single session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    stats = session_stats(session)
    click.echo(f"Session : {session.name}")
    click.echo(f"Total steps      : {stats['total_steps']}")
    click.echo(f"Unique commands  : {stats['unique_commands']}")
    click.echo(f"Steps with notes : {stats['steps_with_notes']}")
    click.echo(f"Top command      : {stats['top_command'] or 'n/a'}")
    click.echo(f"Most active day  : {stats['most_active_day'] or 'n/a'}")


@stats_cmd.command("global")
def global_stats():
    """Show aggregate statistics across all sessions."""
    store = _get_store()
    names = store.list_sessions()
    if not names:
        click.echo("No sessions found.")
        return
    sessions = [store.load(n) for n in names if store.load(n)]
    avg = average_steps_per_session(sessions)
    freq = command_frequency(sessions)
    top = list(freq.items())[:5]
    click.echo(f"Total sessions   : {len(sessions)}")
    click.echo(f"Avg steps/session: {avg:.1f}")
    if top:
        click.echo("Top commands:")
        for cmd, count in top:
            click.echo(f"  {cmd}: {count}")
