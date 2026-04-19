"""Tests for breadcrumb.reminder."""

import pytest
from datetime import date

from breadcrumb.reminder import (
    set_reminder,
    is_due,
    list_due,
    format_reminder,
    ReminderError,
    Reminder,
)


def test_set_reminder_basic():
    r = set_reminder("abc", "2030-01-15", "check this")
    assert r.session_id == "abc"
    assert r.due == date(2030, 1, 15)
    assert r.note == "check this"


def test_set_reminder_strips_whitespace():
    r = set_reminder("  sid  ", "2030-06-01", "  note  ")
    assert r.session_id == "sid"
    assert r.note == "note"


def test_set_reminder_invalid_date_raises():
    with pytest.raises(ReminderError, match="Invalid date"):
        set_reminder("sid", "not-a-date")


def test_set_reminder_empty_session_raises():
    with pytest.raises(ReminderError):
        set_reminder("", "2030-01-01")


def test_is_due_past_date():
    r = Reminder(session_id="x", due=date(2000, 1, 1))
    assert is_due(r, today=date(2024, 1, 1)) is True


def test_is_due_future_date():
    r = Reminder(session_id="x", due=date(2099, 1, 1))
    assert is_due(r, today=date(2024, 1, 1)) is False


def test_is_due_today():
    today = date(2024, 6, 15)
    r = Reminder(session_id="x", due=today)
    assert is_due(r, today=today) is True


def test_list_due_filters_correctly():
    today = date(2024, 6, 15)
    reminders = [
        Reminder("a", due=date(2024, 6, 14)),
        Reminder("b", due=date(2024, 6, 15)),
        Reminder("c", due=date(2024, 6, 16)),
    ]
    due = list_due(reminders, today)
    assert len(due) == 2
    assert due[0].session_id == "a"
    assert due[1].session_id == "b"


def test_format_reminder_due():
    r = Reminder("mysession", due=date(2024, 1, 1), note="urgent")
    out = format_reminder(r, today=date(2024, 6, 1))
    assert "[DUE]" in out
    assert "mysession" in out
    assert "urgent" in out


def test_format_reminder_not_due():
    r = Reminder("mysession", due=date(2099, 1, 1))
    out = format_reminder(r, today=date(2024, 1, 1))
    assert "[DUE]" not in out


def test_roundtrip_to_from_dict():
    r = Reminder("sid", due=date(2025, 3, 10), note="hello")
    r2 = Reminder.from_dict(r.to_dict())
    assert r2.session_id == r.session_id
    assert r2.due == r.due
    assert r2.note == r.note
