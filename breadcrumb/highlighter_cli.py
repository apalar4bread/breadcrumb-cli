import click
from breadcrumb.store import SessionStore
from breadcrumb.highlighter import highlight_command, strip_highlights


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("highlight")
def highlight_cmd():
    """Highlight commands in a session for display."""


@highlight_cmd.command("show")
@click.argument("session_id")
@click.option("--no-color", is_flag=True, default=False, help="Disable color output.")
def show_highlighted(session_id: str, no_color: bool):
    """Show session steps with syntax highlighting."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    for i, step in enumerate(session.steps, 1):
        highlighted = highlight_command(step.command, enabled=not no_color)
        note_part = f"  # {step.note}" if step.note else ""
        click.echo(f"{i:>3}. {highlighted}{note_part}")


@highlight_cmd.command("strip")
@click.argument("session_id")
def show_stripped(session_id: str):
    """Show session steps with all highlight markup stripped."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    for i, step in enumerate(session.steps, 1):
        plain = strip_highlights(step.command)
        click.echo(f"{i:>3}. {plain}")
