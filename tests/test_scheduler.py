import pytest
from breadcrumb.scheduler import (
    Schedule, set_schedule, disable_schedule, enable_schedule,
    describe_schedule, ScheduleError
)


def test_set_schedule_valid():
    s = set_schedule("my-session", "daily")
    assert s.session_id == "my-session"
    assert s.interval == "daily"
    assert s.enabled is True


def test_set_schedule_normalizes_case():
    s = set_schedule("s1", "HOURLY")
    assert s.interval == "hourly"


def test_set_schedule_invalid_interval():
    with pytest.raises(ScheduleError, match="Invalid interval"):
        set_schedule("s1", "monthly")


def test_set_schedule_empty_session_raises():
    with pytest.raises(ScheduleError):
        set_schedule("", "daily")


def test_set_schedule_with_notes():
    s = set_schedule("s1", "weekly", notes="run every monday")
    assert s.notes == "run every monday"


def test_disable_schedule():
    s = set_schedule("s1", "daily")
    disable_schedule(s)
    assert s.enabled is False


def test_enable_schedule():
    s = set_schedule("s1", "daily")
    disable_schedule(s)
    enable_schedule(s)
    assert s.enabled is True


def test_describe_schedule_basic():
    s = set_schedule("s1", "hourly")
    desc = describe_schedule(s)
    assert "s1" in desc
    assert "hourly" in desc
    assert "enabled" in desc


def test_describe_schedule_with_notes():
    s = set_schedule("s1", "daily", notes="important")
    desc = describe_schedule(s)
    assert "important" in desc


def test_roundtrip_serialization():
    s = set_schedule("s1", "weekly", notes="test")
    s2 = Schedule.from_dict(s.to_dict())
    assert s2.session_id == s.session_id
    assert s2.interval == s.interval
    assert s2.notes == s.notes
