"""Reminder module: attach due-date reminders to sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional

DATE_FMT = "%Y-%m-%d"


class ReminderError(Exception):
    pass


@dataclass
class Reminder:
    session_id: str
    due: date
    note: str = ""

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "due": self.due.strftime(DATE_FMT),
            "note": self.note,
        }

    @staticmethod
    def from_dict(d: dict) -> "Reminder":
        return Reminder(
            session_id=d["session_id"],
            due=datetime.strptime(d["due"], DATE_FMT).date(),
            note=d.get("note", ""),
        )


def set_reminder(session_id: str, due_str: str, note: str = "") -> Reminder:
    if not session_id or not session_id.strip():
        raise ReminderError("session_id must not be empty")
    try:
        due = datetime.strptime(due_str.strip(), DATE_FMT).date()
    except ValueError:
        raise ReminderError(f"Invalid date format '{due_str}'. Use YYYY-MM-DD.")
    return Reminder(session_id=session_id.strip(), due=due, note=note.strip())


def is_due(reminder: Reminder, today: Optional[date] = None) -> bool:
    today = today or date.today()
    return reminder.due <= today


def list_due(reminders: List[Reminder], today: Optional[date] = None) -> List[Reminder]:
    return [r for r in reminders if is_due(r, today)]


def format_reminder(reminder: Reminder, today: Optional[date] = None) -> str:
    due_label = " [DUE]" if is_due(reminder, today) else ""
    note_part = f" — {reminder.note}" if reminder.note else ""
    return f"[{reminder.due}]{due_label} {reminder.session_id}{note_part}"
