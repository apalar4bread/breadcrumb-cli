"""Tests for breadcrumb.optimizer."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.optimizer import (
    optimize_session,
    format_optimize_result,
    OptimizerError,
    Suggestion,
)


def make_session(commands, name="test-session"):
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_optimize_empty_session_raises():
    s = Session(name="empty")
    with pytest.raises(OptimizerError, match="no steps"):
        optimize_session(s)


def test_optimize_clean_session_no_suggestions():
    s = make_session(["git status", "git add .", "git commit -m 'msg'"])
    result = optimize_session(s)
    assert not result.has_suggestions
    assert result.session_name == "test-session"


def test_optimize_detects_consecutive_duplicate():
    s = make_session(["ls", "ls", "pwd"])
    result = optimize_session(s)
    assert result.has_suggestions
    dupes = [sg for sg in result.suggestions if "Duplicate" in sg.reason]
    assert len(dupes) == 1
    assert dupes[0].step_index == 1


def test_optimize_consecutive_duplicate_case_insensitive():
    s = make_session(["LS", "ls"])
    result = optimize_session(s)
    dupes = [sg for sg in result.suggestions if "Duplicate" in sg.reason]
    assert len(dupes) == 1


def test_optimize_detects_cd_then_ls():
    s = make_session(["cd /tmp", "ls"])
    result = optimize_session(s)
    cd_suggestions = [sg for sg in result.suggestions if "cd" in sg.reason]
    assert len(cd_suggestions) == 1
    assert "&&" in cd_suggestions[0].suggestion


def test_optimize_cd_ls_la_also_triggers():
    s = make_session(["cd /home/user", "ls -la"])
    result = optimize_session(s)
    cd_suggestions = [sg for sg in result.suggestions if "cd" in sg.reason]
    assert len(cd_suggestions) == 1


def test_optimize_cd_without_ls_no_suggestion():
    s = make_session(["cd /tmp", "pwd"])
    result = optimize_session(s)
    cd_suggestions = [sg for sg in result.suggestions if "cd" in sg.reason]
    assert len(cd_suggestions) == 0


def test_optimize_detects_non_consecutive_repeat():
    s = make_session(["docker ps", "git status", "docker ps"])
    result = optimize_session(s)
    repeat_suggestions = [sg for sg in result.suggestions if "already used" in sg.reason]
    assert len(repeat_suggestions) == 1
    assert repeat_suggestions[0].step_index == 2


def test_optimize_non_consecutive_repeat_references_original_step():
    s = make_session(["make build", "echo done", "make build"])
    result = optimize_session(s)
    repeat_suggestions = [sg for sg in result.suggestions if "already used" in sg.reason]
    assert "step 1" in repeat_suggestions[0].reason


def test_format_optimize_result_clean():
    s = make_session(["echo hello"])
    result = optimize_session(s)
    output = format_optimize_result(result)
    assert "No suggestions" in output
    assert "test-session" in output


def test_format_optimize_result_with_suggestions():
    s = make_session(["ls", "ls"])
    result = optimize_session(s)
    output = format_optimize_result(result)
    assert "Step 2" in output
    assert "Duplicate" in output
