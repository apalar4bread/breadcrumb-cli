"""CLI commands for session activity streaks."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.streaker import compute_streak, format_streak


def _get_store(path=None):
    return SessionStore(path) if path else SessionStore()


@click.group(name="streak")
def streak_cmd():
    """View your session activity streaks."""


@streak_cmd.command(name="show")
@click.option("--store-path", default=None, hidden=True)
def show_streak(store_path):
    """Show current and longest activity streaks."""
    store = _get_store(store_path)
    sessions = [store.load(sid) for sid in store.list_sessions()]
    if not sessions:
        click.echo("No sessions found.")
        return
    result = compute_streak(sessions)
    click.echo(format_streak(result))


@streak_cmd.command(name="summary")
@click.option("--store-path", default=None, hidden=True)
def summary(store_path):
    """Show a compact streak summary line."""
    store = _get_store(store_path)
    sessions = [store.load(sid) for sid in store.list_sessions()]
    result = compute_streak(sessions)
    click.echo(
        f"🔥 Streak: {result.current_streak} day(s) current, "
        f"{result.longest_streak} day(s) best, "
        f"{len(result.active_days)} total active day(s)."
    )
