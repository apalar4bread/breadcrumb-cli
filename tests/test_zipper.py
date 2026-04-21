"""Tests for breadcrumb.zipper."""

import pytest

from breadcrumb.session import Session
from breadcrumb.zipper import ZipError, ZipResult, format_zip_result, zip_sessions


def make_session(name: str, commands: list[str]) -> Session:
    s = Session(name=name)
    for cmd in commands:
        s.steps.append(__import__("breadcrumb.session", fromlist=["Step"]).Step(command=cmd))
    return s


# --- basic zipping ---

def test_zip_alternates_steps():
    left = make_session("A", ["echo a", "echo c"])
    right = make_session("B", ["echo b", "echo d"])
    result = zip_sessions(left, right)
    commands = [s.command for s in result.session.steps]
    assert commands == ["echo a", "echo b", "echo c", "echo d"]


def test_zip_left_longer():
    left = make_session("A", ["a1", "a2", "a3"])
    right = make_session("B", ["b1"])
    result = zip_sessions(left, right)
    commands = [s.command for s in result.session.steps]
    assert commands == ["a1", "b1", "a2", "a3"]


def test_zip_right_longer():
    left = make_session("A", ["a1"])
    right = make_session("B", ["b1", "b2", "b3"])
    result = zip_sessions(left, right)
    commands = [s.command for s in result.session.steps]
    assert commands == ["a1", "b1", "b2", "b3"]


def test_zip_empty_sessions():
    left = make_session("A", [])
    right = make_session("B", [])
    result = zip_sessions(left, right)
    assert result.total_steps == 0


# --- counts ---

def test_zip_result_counts():
    left = make_session("A", ["x", "y"])
    right = make_session("B", ["p"])
    result = zip_sessions(left, right)
    assert result.left_count == 2
    assert result.right_count == 1
    assert result.total_steps == 3


# --- naming ---

def test_zip_default_name():
    left = make_session("Alpha", ["a"])
    right = make_session("Beta", ["b"])
    result = zip_sessions(left, right)
    assert result.session.name == "Alpha + Beta"


def test_zip_custom_name():
    left = make_session("Alpha", ["a"])
    right = make_session("Beta", ["b"])
    result = zip_sessions(left, right, name="Combined")
    assert result.session.name == "Combined"


# --- tags ---

def test_zip_unions_tags():
    left = make_session("A", ["a"])
    left.tags = ["dev", "infra"]
    right = make_session("B", ["b"])
    right.tags = ["infra", "prod"]
    result = zip_sessions(left, right)
    assert set(result.session.tags) == {"dev", "infra", "prod"}


# --- strict mode ---

def test_zip_strict_equal_lengths():
    left = make_session("A", ["a", "b"])
    right = make_session("B", ["x", "y"])
    result = zip_sessions(left, right, strict=True)
    assert result.total_steps == 4


def test_zip_strict_unequal_raises():
    left = make_session("A", ["a", "b", "c"])
    right = make_session("B", ["x"])
    with pytest.raises(ZipError, match="strict mode"):
        zip_sessions(left, right, strict=True)


# --- step independence ---

def test_zip_steps_are_copies():
    left = make_session("A", ["original"])
    right = make_session("B", ["other"])
    result = zip_sessions(left, right)
    result.session.steps[0].command = "mutated"
    assert left.steps[0].command == "original"


# --- format ---

def test_format_zip_result_contains_name():
    left = make_session("A", ["a"])
    right = make_session("B", ["b"])
    result = zip_sessions(left, right)
    text = format_zip_result(result)
    assert "A + B" in text
    assert "2" in text
