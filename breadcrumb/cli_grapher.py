"""CLI commands for the grapher module."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.grapher import build_graph, format_graph, GraphError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("graph")
def graph_cmd():
    """Visualise session steps as a dependency graph."""


@graph_cmd.command("show")
@click.argument("session_name")
@click.option("--no-edges", is_flag=True, default=False, help="Disable sequential edges.")
def show_graph(session_name: str, no_edges: bool):
    """Print the graph for a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = build_graph(session, link_sequential=not no_edges)
    except GraphError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    click.echo(format_graph(result))


@graph_cmd.command("summary")
@click.argument("session_name")
def graph_summary(session_name: str):
    """Print a one-line graph summary for a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        result = build_graph(session)
    except GraphError as exc:
        click.echo(str(exc), err=True)
        raise SystemExit(1)
    click.echo(result.summary())
