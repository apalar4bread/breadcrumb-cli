import click
from breadcrumb.store import SessionStore
from breadcrumb.splitter import split_session, split_summary, SplitError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("split")
def split_cmd():
    """Split a session into two parts at a given step index."""


@split_cmd.command("run")
@click.argument("session_id")
@click.argument("index", type=int)
@click.option("--name-a", default=None, help="Name for the first part.")
@click.option("--name-b", default=None, help="Name for the second part.")
@click.option("--save", is_flag=True, default=False, help="Persist both parts.")
def run_split(session_id: str, index: int, name_a, name_b, save: bool):
    """Split SESSION_ID at INDEX (1-based)."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = split_session(session, index, name_a=name_a, name_b=name_b)
    except SplitError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(split_summary(result))

    if save:
        store.save(result.part_a)
        store.save(result.part_b)
        click.echo(f"Saved '{result.part_a.name}' and '{result.part_b.name}'.")


@split_cmd.command("preview")
@click.argument("session_id")
@click.argument("index", type=int)
def preview_split(session_id: str, index: int):
    """Preview what a split at INDEX would look like without saving."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    try:
        result = split_session(session, index)
    except SplitError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    click.echo(f"Part A — '{result.part_a.name}': {len(result.part_a.steps)} step(s)")
    for i, step in enumerate(result.part_a.steps, 1):
        click.echo(f"  {i}. {step.command}")

    click.echo(f"Part B — '{result.part_b.name}': {len(result.part_b.steps)} step(s)")
    for i, step in enumerate(result.part_b.steps, 1):
        click.echo(f"  {i}. {step.command}")
