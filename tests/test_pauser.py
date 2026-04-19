import pytest
from breadcrumb.session import Session
from breadcrumb.pauser import (
    pause_session,
    resume_session,
    is_paused,
    list_paused,
    format_pause_status,
    PauseError,
)


def make_session(name="test-session"):
    return Session(name=name)


def test_pause_session_sets_metadata():
    s = make_session()
    pause_session(s)
    assert s.metadata.get("paused") is True


def test_pause_already_paused_raises():
    s = make_session()
    pause_session(s)
    with pytest.raises(PauseError, match="already paused"):
        pause_session(s)


def test_resume_session_removes_flag():
    s = make_session()
    pause_session(s)
    resume_session(s)
    assert "paused" not in s.metadata


def test_resume_not_paused_raises():
    s = make_session()
    with pytest.raises(PauseError, match="not paused"):
        resume_session(s)


def test_is_paused_false_by_default():
    s = make_session()
    assert not is_paused(s)


def test_is_paused_true_after_pause():
    s = make_session()
    pause_session(s)
    assert is_paused(s)


def test_list_paused_returns_only_paused():
    s1 = make_session("a")
    s2 = make_session("b")
    s3 = make_session("c")
    pause_session(s1)
    pause_session(s3)
    result = list_paused([s1, s2, s3])
    assert result == [s1, s3]


def test_list_paused_empty():
    sessions = [make_session("x"), make_session("y")]
    assert list_paused(sessions) == []


def test_format_pause_status_paused():
    s = make_session("my-session")
    pause_session(s)
    assert "paused" in format_pause_status(s)
    assert "my-session" in format_pause_status(s)


def test_format_pause_status_active():
    s = make_session("my-session")
    assert "active" in format_pause_status(s)
