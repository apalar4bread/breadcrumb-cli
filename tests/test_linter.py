"""Tests for breadcrumb.linter."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.linter import (
    lint_session,
    format_lint_result,
    LintResult,
    LintIssue,
    LINT_RULES,
)


def make_session(steps=None):
    s = Session(id="s1", name="test-session")
    for cmd, note in (steps or []):
        s.steps.append(Step(command=cmd, note=note))
    return s


def test_lint_clean_session_no_issues():
    s = make_session([("git status", "check status"), ("git pull", "pull latest")])
    result = lint_session(s)
    assert result.passed
    assert result.issues == []


def test_lint_no_note_flagged():
    s = make_session([("git status", "")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "no_note" in rules


def test_lint_long_command_flagged():
    long_cmd = "echo " + "x" * 120
    s = make_session([(long_cmd, "a note")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "long_command" in rules


def test_lint_trailing_whitespace_flagged():
    s = make_session([("git status  ", "note")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "trailing_whitespace" in rules


def test_lint_all_caps_command_flagged():
    s = make_session([("CLEAR", "note")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "all_caps_command" in rules


def test_lint_duplicate_consecutive_flagged():
    s = make_session([("git status", "note"), ("git status", "note2")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "duplicate_consecutive" in rules


def test_lint_duplicate_consecutive_case_insensitive():
    s = make_session([("Git Status", "note"), ("git status", "note2")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "duplicate_consecutive" in rules


def test_lint_non_consecutive_duplicates_not_flagged():
    s = make_session([("git status", "a"), ("git pull", "b"), ("git status", "c")])
    result = lint_session(s)
    rules = [i.rule for i in result.issues]
    assert "duplicate_consecutive" not in rules


def test_lint_with_specific_rules_only():
    s = make_session([("git status  ", "")])
    result = lint_session(s, rules=["trailing_whitespace"])
    rules = [i.rule for i in result.issues]
    assert "trailing_whitespace" in rules
    assert "no_note" not in rules


def test_lint_result_summary_passed():
    s = make_session([("git status", "note")])
    result = lint_session(s)
    assert "no issues" in result.summary()


def test_lint_result_summary_with_issues():
    s = make_session([("git status", "")])
    result = lint_session(s)
    assert "issue" in result.summary()


def test_format_lint_result_includes_rule():
    s = make_session([("git status", "")])
    result = lint_session(s)
    output = format_lint_result(result)
    assert "no_note" in output


def test_lint_issue_str():
    issue = LintIssue(step_index=2, rule="no_note", message="missing note")
    assert "Step 3" in str(issue)
    assert "no_note" in str(issue)
