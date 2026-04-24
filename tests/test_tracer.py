"""Tests for breadcrumb/tracer.py"""
import pytest
from breadcrumb.session import Session, Step
from breadcrumb.tracer import (
    TracerError,
    TraceLink,
    TraceResult,
    trace_session,
    format_trace,
)


def make_session(*commands, notes=None) -> Session:
    notes = notes or [None] * len(commands)
    s = Session(name="test-session")
    for cmd, note in zip(commands, notes):
        s.steps.append(Step(command=cmd, note=note))
    return s


def test_trace_finds_matching_steps():
    s = make_session("git status", "echo hello", "git commit -m 'x'")
    result = trace_session(s, "git")
    assert result.length == 2
    assert result.chain[0].command == "git status"
    assert result.chain[1].command == "git commit -m 'x'"


def test_trace_no_matches_returns_empty_chain():
    s = make_session("ls -la", "echo hi")
    result = trace_session(s, "docker")
    assert result.length == 0
    assert result.session_name == "test-session"


def test_trace_parent_index_links_correctly():
    s = make_session("git init", "ls", "git add .", "pwd", "git push")
    result = trace_session(s, "git")
    assert result.chain[0].parent_index is None
    assert result.chain[1].parent_index == 0  # step index 0
    assert result.chain[2].parent_index == 2  # step index 2


def test_trace_case_insensitive_by_default():
    s = make_session("GIT status", "echo hi")
    result = trace_session(s, "git")
    assert result.length == 1


def test_trace_case_sensitive_no_match():
    s = make_session("GIT status")
    result = trace_session(s, "git", case_sensitive=True)
    assert result.length == 0


def test_trace_case_sensitive_match():
    s = make_session("git status")
    result = trace_session(s, "git", case_sensitive=True)
    assert result.length == 1


def test_trace_empty_keyword_raises():
    s = make_session("ls")
    with pytest.raises(TracerError):
        trace_session(s, "")


def test_trace_blank_keyword_raises():
    s = make_session("ls")
    with pytest.raises(TracerError):
        trace_session(s, "   ")


def test_trace_preserves_note():
    s = make_session("git log", notes=["check history"])
    result = trace_session(s, "git")
    assert result.chain[0].note == "check history"


def test_format_trace_no_matches():
    s = make_session("ls")
    result = trace_session(s, "docker")
    output = format_trace(result)
    assert "No matching steps" in output
    assert "test-session" in output


def test_format_trace_with_matches():
    s = make_session("git init", "git add .", notes=[None, None])
    result = trace_session(s, "git")
    output = format_trace(result)
    assert "git init" in output
    assert "git add ." in output
    assert "test-session" in output


def test_trace_link_to_dict():
    link = TraceLink(step_index=2, command="git push", note="deploy", parent_index=0)
    d = link.to_dict()
    assert d["step_index"] == 2
    assert d["command"] == "git push"
    assert d["note"] == "deploy"
    assert d["parent_index"] == 0
