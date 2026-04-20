"""Tests for breadcrumb.redactor."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.redactor import (
    redact_text,
    redact_step,
    redact_session,
    DEFAULT_PATTERNS,
    REDACT_PLACEHOLDER,
)


def make_step(command: str, note: str = None) -> Step:
    return Step(command=command, note=note)


def make_session(steps=None) -> Session:
    s = Session(name="test-session")
    for st in (steps or []):
        s.steps.append(st)
    return s


# --- redact_text ---

def test_redact_text_no_match():
    assert redact_text("ls -la", DEFAULT_PATTERNS) == "ls -la"


def test_redact_text_password_equals():
    result = redact_text("connect password=secret123", DEFAULT_PATTERNS)
    assert REDACT_PLACEHOLDER in result
    assert "secret123" not in result


def test_redact_text_token_flag():
    result = redact_text("curl --token abc123", DEFAULT_PATTERNS)
    assert REDACT_PLACEHOLDER in result
    assert "abc123" not in result


def test_redact_text_bearer():
    result = redact_text("Authorization: Bearer eyJhbGciOiJIUzI1", DEFAULT_PATTERNS)
    assert REDACT_PLACEHOLDER in result


def test_redact_text_custom_pattern():
    result = redact_text("export MY_VAR=hello", [r"MY_VAR=\S+"])
    assert REDACT_PLACEHOLDER in result
    assert "hello" not in result


# --- redact_step ---

def test_redact_step_no_change():
    step = make_step("git status")
    result = redact_step(step)
    assert not result.changed
    assert result.redacted_command == "git status"


def test_redact_step_command_changed():
    step = make_step("login --password hunter2")
    result = redact_step(step)
    assert result.changed
    assert "hunter2" not in result.redacted_command
    assert REDACT_PLACEHOLDER in result.redacted_command


def test_redact_step_note_changed():
    step = make_step("echo hi", note="api_key=supersecret")
    result = redact_step(step)
    assert result.changed
    assert "supersecret" not in result.redacted_note


def test_redact_step_does_not_mutate():
    step = make_step("login --password abc")
    redact_step(step)
    assert "abc" in step.command


# --- redact_session ---

def test_redact_session_returns_new_object():
    session = make_session([make_step("echo hello")])
    new_session = redact_session(session)
    assert new_session is not session


def test_redact_session_cleans_commands():
    session = make_session([
        make_step("deploy --token secret99"),
        make_step("ls"),
    ])
    new_session = redact_session(session)
    assert "secret99" not in new_session.steps[0].command
    assert new_session.steps[1].command == "ls"


def test_redact_session_preserves_metadata():
    session = make_session([make_step("echo ok")])
    session.metadata["author"] = "alice"
    new_session = redact_session(session)
    assert new_session.metadata["author"] == "alice"


def test_redact_session_in_place_mutates():
    step = make_step("connect password=topsecret")
    session = make_session([step])
    result = redact_session(session, in_place=True)
    assert result is session
    assert "topsecret" not in session.steps[0].command
