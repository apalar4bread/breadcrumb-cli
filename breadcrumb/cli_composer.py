"""CLI commands for composing sessions from cherry-picked steps."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.composer import compose_session, compose_summary, ComposeError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("compose")
def compose_cmd():
    """Build a new session by cherry-picking steps from existing sessions."""


@compose_cmd.command("build")
@click.option("--name", required=True, help="Name for the new composed session.")
@click.option(
    "--pick",
    multiple=True,
    required=True,
    metavar="SESSION_ID:INDEX",
    help="Pick a step by session ID and 0-based index. Repeatable.",
)
def build_cmd(name: str, pick):
    """Compose a new session from cherry-picked steps.

    Example:
      breadcrumb compose build --name deploy --pick abc123:0 --pick def456:2
    """
    store = _get_store()
    sources_map = {}

    for token in pick:
        if ":" not in token:
            raise click.BadParameter(
                f"Expected SESSION_ID:INDEX, got '{token}'", param_hint="--pick"
            )
        sid, _, raw_idx = token.partition(":")
        try:
            idx = int(raw_idx)
        except ValueError:
            raise click.BadParameter(
                f"Index must be an integer, got '{raw_idx}'", param_hint="--pick"
            )
        sources_map.setdefault(sid, []).append(idx)

    sources = []
    for sid, indices in sources_map.items():
        session = store.load(sid)
        if session is None:
            raise click.ClickException(f"Session '{sid}' not found.")
        sources.append((session, indices))

    try:
        result = compose_session(sources, name=name)
    except ComposeError as exc:
        raise click.ClickException(str(exc))

    store.save(result)
    summary = compose_summary(result, sources)
    click.echo(summary)
    click.echo(f"Session ID: {result.id}")
