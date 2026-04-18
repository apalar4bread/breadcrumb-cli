"""CLI commands for step labeling."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.labeler import set_label, clear_label, get_label, find_by_label, LabelError, VALID_LABELS


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("label")
def label_cmd():
    """Manage step labels (priority/status)."""


@label_cmd.command("set")
@click.argument("session_name")
@click.argument("step_index", type=int)
@click.argument("label")
def set_cmd(session_name, step_index, label):
    """Assign a label to a step."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        set_label(session, step_index, label)
        store.save(session)
        click.echo(f"Step {step_index} labeled '{label.strip().lower()}'.")
    except LabelError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_cmd.command("clear")
@click.argument("session_name")
@click.argument("step_index", type=int)
def clear_cmd(session_name, step_index):
    """Remove label from a step."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    try:
        clear_label(session, step_index)
        store.save(session)
        click.echo(f"Label cleared from step {step_index}.")
    except LabelError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@label_cmd.command("find")
@click.argument("session_name")
@click.argument("label")
def find_cmd(session_name, label):
    """Find all steps with a given label."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)
    results = find_by_label(session, label)
    if not results:
        click.echo(f"No steps labeled '{label}'.")
    else:
        for idx, step in results:
            click.echo(f"  [{idx}] {step.command}")
