"""CLI command for exporting sessions to CSV."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.exporter_csv import write_csv


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("export-csv")
def csv_cmd():
    """Export a session to CSV format."""


@csv_cmd.command("run")
@click.argument("session_id")
@click.argument("output")
def run_export(session_id: str, output: str):
    """Export SESSION_ID steps to OUTPUT (.csv file)."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        path = write_csv(session, output)
        click.echo(f"Exported {len(session.steps)} step(s) to {path}")
    except ValueError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
