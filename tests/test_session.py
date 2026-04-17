"""Tests for session tracking core."""

import time
import pytest
from breadcrumb.session import Session, Step


def test_add_step_defaults():
    s = Session(name="test")
    step = s.add_step("echo hello")
    assert len(s.steps) == 1
    assert step.command == "echo hello"
    assert step.exit_code is None
    assert step.note is None


def test_add_step_with_metadata():
    s = Session(name="test")
    step = s.add_step("ls -la", cwd="/tmp", exit_code=0, note="list files")
    assert step.cwd == "/tmp"
    assert step.exit_code == 0
    assert step.note == "list files"


def test_session_serialization_roundtrip():
    s = Session(name="roundtrip")
    s.add_step("git init", cwd="/home/user/project", exit_code=0)
    s.add_step("git add .", cwd="/home/user/project", exit_code=0, note="stage all")

    data = s.to_dict()
    restored = Session.from_dict(data)

    assert restored.name == s.name
    assert len(restored.steps) == 2
    assert restored.steps[1].note == "stage all"


def test_step_timestamp_is_recent():
    before = time.time()
    s = Session(name="ts")
    step = s.add_step("pwd")
    after = time.time()
    assert before <= step.timestamp <= after
