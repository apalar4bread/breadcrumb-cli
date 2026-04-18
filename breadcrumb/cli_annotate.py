"""CLI commands for annotating session steps with comments."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.annotator import annotate_step, clear_annotation, list_annotated, AnnotateError


@click.group("annotate")
def annotate_cmd():
    """Annotate steps with comments."""


def _get_store() -> SessionStore:
    return SessionStore()


@annotate_cmd.command("set")
@click.argument("session_name")
@click.argument("step_index", type=int)
@click.argument("comment")
def set_comment(session_name, step_index, comment):
    """Set a comment on a step."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        annotate_step(session, step_index, comment)
        store.save(session)
        click.echo(f"Annotated step {step_index}: {comment!r}")
    except AnnotateError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@annotate_cmd.command("clear")
@click.argument("session_name")
@click.argument("step_index", type=int)
def clear_comment(session_name, step_index):
    """Clear the comment from a step."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        clear_annotation(session, step_index)
        store.save(session)
        click.echo(f"Cleared annotation on step {step_index}.")
    except AnnotateError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@annotate_cmd.command("list")
@click.argument("session_name")
def list_comments(session_name):
    """List all annotated steps in a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    annotated = list_annotated(session)
    if not annotated:
        click.echo("No annotated steps.")
        return
    for i, step in annotated:
        click.echo(f"  [{i}] {step.command}  # {step.metadata['comment']}")
