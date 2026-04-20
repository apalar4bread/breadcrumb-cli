"""CLI command for exporting sessions to YAML."""

import click

from breadcrumb.store import SessionStore
from breadcrumb.exporter_yaml import export_to_yaml, write_yaml, YamlExportError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="yaml")
def yaml_cmd():
    """Export a session to YAML format."""


@yaml_cmd.command(name="export")
@click.argument("session_id")
@click.option(
    "--output",
    "-o",
    default=None,
    help="Output file path (.yaml or .yml). Prints to stdout if omitted.",
)
@click.option("--indent", default=2, show_default=True, help="YAML indentation level.")
def run_export(session_id: str, output: str, indent: int):
    """Export SESSION_ID to YAML."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        if output:
            path = write_yaml(session, output)
            click.echo(f"Exported to {path}")
        else:
            click.echo(export_to_yaml(session, indent=indent))
    except YamlExportError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)
