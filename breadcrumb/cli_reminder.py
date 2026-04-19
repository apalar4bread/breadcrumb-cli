"""CLI commands for session reminders."""

import click
from datetime import date

from breadcrumb.store import SessionStore
from breadcrumb.reminder import set_reminder, list_due, format_reminder, ReminderError


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("reminder")
def reminder_cmd():
    """Manage session reminders."""


@reminder_cmd.command("set")
@click.argument("session_id")
@click.argument("due_date")
@click.option("--note", default="", help="Optional reminder note.")
def set_cmd(session_id: str, due_date: str, note: str):
    """Set a reminder for SESSION_ID due on DUE_DATE (YYYY-MM-DD)."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        reminder = set_reminder(session_id, due_date, note)
    except ReminderError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    session.metadata["reminder_due"] = str(reminder.due)
    session.metadata["reminder_note"] = reminder.note
    store.save(session)
    click.echo(f"Reminder set: {format_reminder(reminder)}")


@reminder_cmd.command("clear")
@click.argument("session_id")
def clear_cmd(session_id: str):
    """Clear the reminder for SESSION_ID."""
    store = _get_store()
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    session.metadata.pop("reminder_due", None)
    session.metadata.pop("reminder_note", None)
    store.save(session)
    click.echo("Reminder cleared.")


@reminder_cmd.command("due")
def due_cmd():
    """List all sessions with reminders that are due today."""
    store = _get_store()
    sessions = store.list_all()
    today = date.today()
    found = 0
    for session in sessions:
        due_str = session.metadata.get("reminder_due")
        if not due_str:
            continue
        try:
            reminder = set_reminder(session.id, due_str, session.metadata.get("reminder_note", ""))
        except ReminderError:
            continue
        if reminder.due <= today:
            click.echo(format_reminder(reminder, today))
            found += 1
    if found == 0:
        click.echo("No reminders due.")
