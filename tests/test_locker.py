import pytest
from breadcrumb.session import Session
from breadcrumb.locker import (
    lock_session,
    unlock_session,
    is_locked,
    assert_unlocked,
    list_locked,
    LockError,
)


def make_session(name="test"):
    return Session(id="abc", name=name, steps=[], tags=[], metadata={})


def test_lock_session_sets_metadata():
    s = make_session()
    lock_session(s)
    assert s.metadata.get("locked") is True


def test_lock_already_locked_raises():
    s = make_session()
    lock_session(s)
    with pytest.raises(LockError, match="already locked"):
        lock_session(s)


def test_unlock_session_removes_flag():
    s = make_session()
    lock_session(s)
    unlock_session(s)
    assert "locked" not in s.metadata


def test_unlock_not_locked_raises():
    s = make_session()
    with pytest.raises(LockError, match="not locked"):
        unlock_session(s)


def test_is_locked_false_by_default():
    s = make_session()
    assert is_locked(s) is False


def test_is_locked_true_after_lock():
    s = make_session()
    lock_session(s)
    assert is_locked(s) is True


def test_assert_unlocked_passes_when_not_locked():
    s = make_session()
    assert_unlocked(s)  # should not raise


def test_assert_unlocked_raises_when_locked():
    s = make_session()
    lock_session(s)
    with pytest.raises(LockError, match="locked and cannot be modified"):
        assert_unlocked(s)


def test_list_locked_returns_only_locked():
    s1 = make_session("a")
    s2 = make_session("b")
    s3 = make_session("c")
    lock_session(s1)
    lock_session(s3)
    result = list_locked([s1, s2, s3])
    assert result == [s1, s3]


def test_list_locked_empty_when_none_locked():
    sessions = [make_session("x"), make_session("y")]
    assert list_locked(sessions) == []
