import click
from breadcrumb.store import SessionStore
from breadcrumb.scorer import score_session, top_steps


def _get_store() -> SessionStore:
    return SessionStore()


@click.group(name="score")
def score_cmd():
    """Score sessions and steps by quality."""


@score_cmd.command(name="show")
@click.argument("session_name")
def show_score(session_name: str):
    """Show the score breakdown for a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    result = score_session(session)
    click.echo(f"Session: {session.name}")
    click.echo(f"  Total score : {result.total_score}")
    click.echo(f"  Step count  : {len(session.steps)}")
    click.echo(f"  Avg / step  : {result.average_score:.2f}")
    click.echo()
    for i, ss in enumerate(result.step_scores):
        click.echo(f"  [{i}] {ss.command[:40]:<40}  score={ss.score}")


@score_cmd.command(name="top")
@click.argument("session_name")
@click.option("--limit", "-n", default=5, show_default=True, help="Number of top steps to show.")
def top_cmd(session_name: str, limit: int):
    """Show the top-scoring steps in a session."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.", err=True)
        raise SystemExit(1)

    steps = top_steps(session, n=limit)
    click.echo(f"Top {limit} steps in '{session.name}':")
    for rank, ss in enumerate(steps, start=1):
        click.echo(f"  {rank}. [{ss.index}] {ss.command[:50]}  (score={ss.score})")
