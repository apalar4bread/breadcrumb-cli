import pytest
from datetime import datetime, timedelta
from breadcrumb.session import Session, Step
from breadcrumb.profiler import profile_session, format_profile


def make_session(name="test", steps=None):
    s = Session(id="abc", name=name, steps=steps or [], tags=[])
    return s


def make_step(command, note="", offset_seconds=0):
    ts = (datetime(2024, 1, 1, 12, 0, 0) + timedelta(seconds=offset_seconds)).isoformat()
    return Step(command=command, note=note, timestamp=ts, metadata={})


def test_profile_empty_session():
    s = make_session(steps=[])
    r = profile_session(s)
    assert r.total_steps == 0
    assert r.unique_commands == 0
    assert r.top_commands == []
    assert r.duration_seconds is None


def test_profile_step_count():
    steps = [make_step("ls"), make_step("pwd"), make_step("ls")]
    s = make_session(steps=steps)
    r = profile_session(s)
    assert r.total_steps == 3


def test_profile_unique_commands():
    steps = [make_step("ls"), make_step("pwd"), make_step("ls")]
    s = make_session(steps=steps)
    r = profile_session(s)
    assert r.unique_commands == 2


def test_profile_top_commands_sorted():
    steps = [make_step("ls")] * 3 + [make_step("pwd")] * 2 + [make_step("echo")]
    s = make_session(steps=steps)
    r = profile_session(s)
    assert r.top_commands[0][0] == "ls"
    assert r.top_commands[0][1] == 3


def test_profile_duration():
    steps = [make_step("ls", offset_seconds=0), make_step("pwd", offset_seconds=60)]
    s = make_session(steps=steps)
    r = profile_session(s)
    assert r.duration_seconds == 60.0


def test_profile_notes_count():
    steps = [make_step("ls", note="list"), make_step("pwd", note=""), make_step("echo", note="print")]
    s = make_session(steps=steps)
    r = profile_session(s)
    assert r.has_notes == 2


def test_profile_tags_flag():
    s = make_session(steps=[make_step("ls")])
    s.tags = ["deploy"]
    r = profile_session(s)
    assert r.has_tags is True


def test_format_profile_contains_name():
    steps = [make_step("ls")]
    s = make_session(name="my-session", steps=steps)
    r = profile_session(s)
    out = format_profile(r)
    assert "my-session" in out
    assert "Steps" in out


def test_format_profile_empty_no_span():
    s = make_session(steps=[])
    r = profile_session(s)
    out = format_profile(r)
    assert "Span" not in out
