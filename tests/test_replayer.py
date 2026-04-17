import pytest
from unittest.mock import patch, MagicMock
from breadcrumb.session import Session
from breadcrumb.replayer import replay_session, replay_step


@pytest.fixture
def simple_session():
    s = Session(name="test-replay")
    s.add_step("echo hello")
    s.add_step("echo world")
    return s


def test_replay_dry_run_does_not_execute(simple_session):
    results = replay_session(simple_session, dry_run=True, delay=0)
    assert len(results) == 2
    assert all(r["dry_run"] for r in results)
    assert all(r["returncode"] == 0 for r in results)


def test_replay_step_dry_run():
    session = Session(name="s")
    session.add_step("ls -la")
    result = replay_step(session.steps[0], dry_run=True)
    assert result["dry_run"] is True
    assert result["command"] == "ls -la"
    assert result["returncode"] == 0


def test_replay_step_real_success():
    session = Session(name="s")
    session.add_step("echo hi")
    result = replay_step(session.steps[0], dry_run=False)
    assert result["returncode"] == 0
    assert "hi" in result["stdout"]


def test_replay_step_real_failure():
    session = Session(name="s")
    session.add_step("exit 1")
    result = replay_step(session.steps[0], dry_run=False)
    assert result["returncode"] != 0


def test_replay_stops_on_error():
    s = Session(name="err-session")
    s.add_step("exit 1")
    s.add_step("echo should-not-run")
    results = replay_session(s, dry_run=False, delay=0, stop_on_error=True)
    assert len(results) == 1


def test_replay_continues_on_error_when_disabled():
    s = Session(name="err-session")
    s.add_step("exit 1")
    s.add_step("echo hi")
    results = replay_session(s, dry_run=False, delay=0, stop_on_error=False)
    assert len(results) == 2
