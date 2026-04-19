import click
from breadcrumb.store import SessionStore
from breadcrumb.watchdog import WatchdogRule, check_session, format_alerts


def _get_store():
    return SessionStore()


@click.group(name="watch")
def watchdog_cmd():
    """Watch sessions for rule violations."""


@watchdog_cmd.command("check")
@click.argument("session_name")
@click.option("--max-steps", type=int, default=None, help="Maximum allowed steps.")
@click.option("--forbid", multiple=True, help="Forbidden command patterns.")
@click.option("--case-sensitive", is_flag=True, default=False)
def check_cmd(session_name, max_steps, forbid, case_sensitive):
    """Check a session against watchdog rules."""
    store = _get_store()
    session = store.load(session_name)
    if session is None:
        click.echo(f"Session '{session_name}' not found.")
        raise SystemExit(1)

    rule = WatchdogRule(
        max_steps=max_steps,
        forbidden_patterns=list(forbid),
        case_sensitive=case_sensitive
    )
    alerts = check_session(session, rule)
    if alerts:
        click.echo(format_alerts(alerts))
        raise SystemExit(2)
    else:
        click.echo("All clear. No alerts.")
