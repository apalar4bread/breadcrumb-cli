"""CLI commands for session digest / fingerprinting."""

import click

from breadcrumb.digester import digest_session, digests_match, format_digest
from breadcrumb.store import SessionStore


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("digest")
def digest_cmd():
    """Compute and compare session fingerprints."""


@digest_cmd.command("show")
@click.argument("session_id")
def show_digest(session_id: str):
    """Show the digest/fingerprint for a session."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    result = digest_session(session)
    click.echo(format_digest(result))


@digest_cmd.command("compare")
@click.argument("session_id_a")
@click.argument("session_id_b")
def compare_digests(session_id_a: str, session_id_b: str):
    """Compare fingerprints of two sessions."""
    store = _get_store()
    a = store.load(session_id_a)
    b = store.load(session_id_b)

    if a is None:
        click.echo(f"Session '{session_id_a}' not found.", err=True)
        raise SystemExit(1)
    if b is None:
        click.echo(f"Session '{session_id_b}' not found.", err=True)
        raise SystemExit(1)

    da = digest_session(a)
    db = digest_session(b)

    click.echo(f"A: {da.session_name}  [{da.short()}]")
    click.echo(f"B: {db.session_name}  [{db.short()}]")

    if digests_match(da, db):
        click.echo("Result: IDENTICAL fingerprints")
    else:
        click.echo("Result: DIFFERENT fingerprints")
