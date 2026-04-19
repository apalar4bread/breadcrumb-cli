"""CLI command for validating a session."""

import click
from breadcrumb.store import SessionStore
from breadcrumb.validator import validate_session, format_validation_result


@click.command("validate")
@click.argument("session_id")
@click.option("--quiet", "-q", is_flag=True, help="Only output on failure.")
@click.pass_context
def validate_cmd(ctx, session_id, quiet):
    """Validate a session for integrity issues."""
    store: SessionStore = ctx.obj["store"]
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        ctx.exit(1)
        return

    result = validate_session(session)

    if not quiet or not result.valid:
        click.echo(format_validation_result(result))

    if not result.valid:
        ctx.exit(2)
