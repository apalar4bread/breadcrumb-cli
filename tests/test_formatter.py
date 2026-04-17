"""Tests for breadcrumb.formatter module."""

import pytest
from breadcrumb.session import Session
from breadcrumb.formatter import format_step, format_session, format_session_list


@pytest.fixture
def simple_session():
    s = Session(name="demo")
    s.add_step("echo hello", cwd="/home/user")
    s.add_step("ls -la", cwd="/tmp", metadata={"note": "listing files"})
    return s


def test_format_step_basic(simple_session):
    step = simple_session.steps[0]
    result = format_step(step, 1)
    assert "[1]" in result
    assert "echo hello" in result
    assert "/home/user" in result


def test_format_step_with_metadata(simple_session):
    step = simple_session.steps[1]
    result = format_step(step, 2)
    assert "note" in result
    assert "listing files" in result


def test_format_session_no_verbose(simple_session):
    result = format_session(simple_session, verbose=False)
    assert "demo" in result
    assert "Steps   : 2" in result
    assert "echo hello" not in result


def test_format_session_verbose(simple_session):
    result = format_session(simple_session, verbose=True)
    assert "echo hello" in result
    assert "ls -la" in result
    assert "[1]" in result
    assert "[2]" in result


def test_format_session_verbose_no_steps():
    s = Session(name="empty")
    result = format_session(s, verbose=True)
    assert "Steps   : 0" in result
    assert "[1]" not in result


def test_format_session_list_empty():
    result = format_session_list([])
    assert "No sessions found" in result


def test_format_session_list_with_items():
    result = format_session_list(["alpha", "beta", "gamma"])
    assert "1. alpha" in result
    assert "3. gamma" in result
    assert "Sessions:" in result
