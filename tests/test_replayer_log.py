"""Tests for breadcrumb.replayer_log."""

from datetime import datetime, timezone

import pytest

from breadcrumb.replayer_log import (
    ReplayLog,
    ReplayLogEntry,
    create_log,
    format_log,
)
from breadcrumb.session import Session


def make_session(name: str = "demo") -> Session:
    s = Session(name=name)
    return s


def make_entry(
    index: int = 0,
    command: str = "echo hi",
    exit_code: int = 0,
    skipped: bool = False,
) -> ReplayLogEntry:
    return ReplayLogEntry(
        step_index=index,
        command=command,
        exit_code=exit_code,
        stdout="hi" if exit_code == 0 else "",
        stderr="" if exit_code == 0 else "error",
        skipped=skipped,
    )


def test_create_log_uses_session_fields():
    s = make_session("my-session")
    log = create_log(s)
    assert log.session_id == s.id
    assert log.session_name == "my-session"
    assert log.entries == []
    assert log.finished_at is None


def test_record_adds_entry():
    log = create_log(make_session())
    entry = make_entry(0, "ls -la")
    log.record(entry)
    assert len(log.entries) == 1
    assert log.entries[0].command == "ls -la"


def test_finish_sets_finished_at():
    log = create_log(make_session())
    assert log.finished_at is None
    log.finish()
    assert log.finished_at is not None
    # should be a valid ISO timestamp
    datetime.fromisoformat(log.finished_at)


def test_success_count():
    log = create_log(make_session())
    log.record(make_entry(0, exit_code=0))
    log.record(make_entry(1, exit_code=0))
    log.record(make_entry(2, exit_code=1))
    assert log.success_count == 2


def test_failure_count():
    log = create_log(make_session())
    log.record(make_entry(0, exit_code=0))
    log.record(make_entry(1, exit_code=127))
    assert log.failure_count == 1


def test_skipped_count():
    log = create_log(make_session())
    log.record(make_entry(0, skipped=True))
    log.record(make_entry(1, skipped=True))
    log.record(make_entry(2, exit_code=0))
    assert log.skipped_count == 2
    assert log.success_count == 1


def test_skipped_not_counted_as_failure():
    log = create_log(make_session())
    log.record(make_entry(0, skipped=True))
    assert log.failure_count == 0


def test_to_dict_roundtrip():
    log = create_log(make_session("roundtrip"))
    log.record(make_entry(0, "git status", exit_code=0))
    log.record(make_entry(1, "git push", exit_code=1))
    log.finish()

    data = log.to_dict()
    restored = ReplayLog.from_dict(data)

    assert restored.session_id == log.session_id
    assert restored.session_name == log.session_name
    assert restored.finished_at == log.finished_at
    assert len(restored.entries) == 2
    assert restored.entries[0].command == "git status"
    assert restored.entries[1].exit_code == 1


def test_entry_to_dict_roundtrip():
    entry = make_entry(3, "make test", exit_code=0)
    data = entry.to_dict()
    restored = ReplayLogEntry.from_dict(data)
    assert restored.step_index == 3
    assert restored.command == "make test"
    assert restored.exit_code == 0


def test_format_log_contains_session_name():
    log = create_log(make_session("my-proj"))
    log.record(make_entry(0, "echo hello", exit_code=0))
    log.finish()
    output = format_log(log)
    assert "my-proj" in output
    assert "echo hello" in output
    assert "OK" in output


def test_format_log_shows_failure():
    log = create_log(make_session())
    log.record(make_entry(0, "bad-cmd", exit_code=127))
    output = format_log(log)
    assert "FAIL" in output


def test_format_log_shows_skipped():
    log = create_log(make_session())
    log.record(make_entry(0, "dry-run-cmd", skipped=True))
    output = format_log(log)
    assert "SKIP" in output
