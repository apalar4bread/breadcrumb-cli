"""Tests for breadcrumb.stamper_validator."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.stamper_validator import (
    validate_stamps,
    format_stamp_validation,
    StampValidationResult,
)


def make_session(commands=None):
    s = Session(name="test-session")
    for cmd in (commands or []):
        s.steps.append(Step(command=cmd))
    return s


def test_no_stamps_returns_zero_checked():
    session = make_session(["echo hello", "ls"])
    result = validate_stamps(session)
    assert result.checked == 0
    assert bool(result) is True


def test_valid_stamp_passes():
    session = make_session(["echo hi"])
    session.steps[0].metadata["stamp"] = "2024-01-15T10:30:00"
    result = validate_stamps(session)
    assert result.checked == 1
    assert bool(result) is True
    assert len(result.issues) == 0


def test_invalid_stamp_format_raises_issue():
    session = make_session(["echo hi"])
    session.steps[0].metadata["stamp"] = "not-a-date"
    result = validate_stamps(session)
    assert result.checked == 1
    assert not bool(result)
    assert any("not a valid ISO" in issue for issue in result.issues)


def test_empty_stamp_string_raises_issue():
    session = make_session(["ls"])
    session.steps[0].metadata["stamp"] = "   "
    result = validate_stamps(session)
    assert not bool(result)
    assert any("empty" in issue for issue in result.issues)


def test_non_string_stamp_raises_issue():
    session = make_session(["pwd"])
    session.steps[0].metadata["stamp"] = 12345
    result = validate_stamps(session)
    assert not bool(result)
    assert len(result.issues) == 1


def test_multiple_steps_mixed_validity():
    session = make_session(["a", "b", "c"])
    session.steps[0].metadata["stamp"] = "2024-06-01T00:00:00"
    session.steps[1].metadata["stamp"] = "bad-date"
    result = validate_stamps(session)
    assert result.checked == 2
    assert len(result.issues) == 1


def test_summary_no_issues():
    session = make_session(["echo"])
    session.steps[0].metadata["stamp"] = "2024-03-10T08:00:00"
    result = validate_stamps(session)
    assert "valid" in result.summary


def test_summary_with_issues():
    session = make_session(["echo"])
    session.steps[0].metadata["stamp"] = "oops"
    result = validate_stamps(session)
    assert "issue" in result.summary


def test_format_stamp_validation_includes_issues():
    session = make_session(["ls"])
    session.steps[0].metadata["stamp"] = "wrong"
    result = validate_stamps(session)
    formatted = format_stamp_validation(result)
    assert "wrong" in formatted or "ISO" in formatted
    assert "\n" in formatted or len(formatted) > 0
