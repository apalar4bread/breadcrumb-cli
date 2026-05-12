"""CLI commands for the session linter."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.linter import lint_session, format_lint_result, LINT_RULES


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("lint")
def lint_cmd():
    """Lint session steps for style and quality issues."""


@lint_cmd.command("check")
@click.argument("session_id")
@click.option(
    "--rule", "-r",
    multiple=True,
    help="Limit to specific rule(s). Can be repeated.",
)
@click.option("--strict", is_flag=True, help="Exit with non-zero code if issues found.")
def check(session_id, rule, strict):
    """Check a session for lint issues."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)

    rules = list(rule) if rule else None
    result = lint_session(session, rules=rules)
    click.echo(format_lint_result(result))

    if strict and not result.passed:
        raise SystemExit(1)


@lint_cmd.command("rules")
def list_rules():
    """List all available lint rules."""
    click.echo("Available lint rules:")
    for r in LINT_RULES:
        click.echo(f"  {r}")


@lint_cmd.command("check-all")
@click.option("--strict", is_flag=True, help="Exit with non-zero code if any issues found.")
def check_all(strict):
    """Lint all sessions in the store."""
    store = _get_store()
    sessions = store.list_sessions()
    if not sessions:
        click.echo("No sessions found.")
        return

    any_issues = False
    for meta in sessions:
        session = store.load(meta["id"])
        if session is None:
            continue
        result = lint_session(session)
        click.echo(format_lint_result(result))
        if not result.passed:
            any_issues = True

    if strict and any_issues:
        raise SystemExit(1)
