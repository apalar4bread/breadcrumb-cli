"""Tests for breadcrumb.deduplicator."""

import pytest

from breadcrumb.session import Session, Step
from breadcrumb.deduplicator import (
    deduplicate_consecutive,
    deduplicate_all,
    DeduplicateResult,
)


def make_session(*commands: str) -> Session:
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


# ---------------------------------------------------------------------------
# deduplicate_consecutive
# ---------------------------------------------------------------------------

def test_consecutive_no_duplicates():
    s = make_session("ls", "pwd", "echo hi")
    result = deduplicate_consecutive(s)
    assert result.removed_count == 0
    assert result.final_count == 3
    assert [st.command for st in result.session.steps] == ["ls", "pwd", "echo hi"]


def test_consecutive_removes_adjacent_dupes():
    s = make_session("ls", "ls", "ls", "pwd")
    result = deduplicate_consecutive(s)
    assert result.removed_count == 2
    assert result.final_count == 2
    assert [st.command for st in result.session.steps] == ["ls", "pwd"]


def test_consecutive_case_insensitive():
    s = make_session("LS", "ls", "Ls")
    result = deduplicate_consecutive(s)
    assert result.removed_count == 2
    assert result.final_count == 1


def test_consecutive_non_adjacent_kept():
    s = make_session("ls", "pwd", "ls")
    result = deduplicate_consecutive(s)
    assert result.removed_count == 0
    assert result.final_count == 3


def test_consecutive_empty_session():
    s = make_session()
    result = deduplicate_consecutive(s)
    assert result.removed_count == 0
    assert result.final_count == 0


def test_consecutive_summary_string():
    s = make_session("git status", "git status", "git log")
    result = deduplicate_consecutive(s)
    assert "1" in result.summary
    assert "→" in result.summary


# ---------------------------------------------------------------------------
# deduplicate_all
# ---------------------------------------------------------------------------

def test_all_removes_non_adjacent_dupes():
    s = make_session("ls", "pwd", "ls")
    result = deduplicate_all(s)
    assert result.removed_count == 1
    assert result.final_count == 2
    assert [st.command for st in result.session.steps] == ["ls", "pwd"]


def test_all_case_insensitive():
    s = make_session("GIT STATUS", "pwd", "git status")
    result = deduplicate_all(s)
    assert result.removed_count == 1
    assert result.final_count == 2


def test_all_no_duplicates():
    s = make_session("a", "b", "c")
    result = deduplicate_all(s)
    assert result.removed_count == 0
    assert result.final_count == 3


def test_all_empty_session():
    s = make_session()
    result = deduplicate_all(s)
    assert result.removed_count == 0
    assert result.final_count == 0


def test_all_result_is_deduplicate_result_instance():
    s = make_session("echo 1", "echo 2")
    result = deduplicate_all(s)
    assert isinstance(result, DeduplicateResult)


def test_all_original_count_reflects_before_removal():
    s = make_session("ls", "ls", "ls")
    result = deduplicate_all(s)
    assert result.original_count == 3
    assert result.final_count == 1
    assert result.removed_count == 2
