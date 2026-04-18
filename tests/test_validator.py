import pytest
from breadcrumb.session import Session, Step
from breadcrumb.validator import (
    validate_step,
    validate_session,
    format_validation_result,
)


def make_step(command="echo hello", note=None):
    s = Step(command=command)
    s.note = note
    return s


def make_session(name="test", steps=None):
    session = Session(name=name)
    for s in (steps or []):
        session.steps.append(s)
    return session


def test_validate_step_valid():
    result = validate_step(make_step())
    assert result.valid
    assert result.errors == []


def test_validate_step_empty_command():
    result = validate_step(make_step(command=""))
    assert not result.valid
    assert any("empty" in e for e in result.errors)


def test_validate_step_blank_command():
    result = validate_step(make_step(command="   "))
    assert not result.valid


def test_validate_step_long_command_warns():
    result = validate_step(make_step(command="x" * 1001))
    assert result.valid  # warning, not error
    assert any("long" in w for w in result.warnings)


def test_validate_step_long_note_warns():
    result = validate_step(make_step(note="n" * 501))
    assert result.valid
    assert any("note" in w for w in result.warnings)


def test_validate_session_valid():
    session = make_session(steps=[make_step()])
    result = validate_session(session)
    assert result.valid


def test_validate_session_no_steps_warns():
    session = make_session(steps=[])
    result = validate_session(session)
    assert result.valid
    assert any("no steps" in w for w in result.warnings)


def test_validate_session_empty_name():
    session = make_session(name="")
    result = validate_session(session)
    assert not result.valid
    assert any("name" in e for e in result.errors)


def test_validate_session_propagates_step_errors():
    session = make_session(steps=[make_step(command="")])
    result = validate_session(session)
    assert not result.valid
    assert any("Step 1" in e for e in result.errors)


def test_format_validation_result_pass():
    from breadcrumb.validator import ValidationResult
    r = ValidationResult(valid=True, warnings=["something long"])
    out = format_validation_result(r)
    assert "✓" in out
    assert "WARN" in out


def test_format_validation_result_fail():
    from breadcrumb.validator import ValidationResult
    r = ValidationResult(valid=False, errors=["bad thing"])
    out = format_validation_result(r)
    assert "✗" in out
    assert "ERROR" in out
