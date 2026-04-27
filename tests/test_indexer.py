"""Tests for breadcrumb.indexer."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.indexer import (
    build_index,
    query_index,
    format_index_entry,
    IndexEntry,
    StepIndex,
)


def make_step(command: str, note: str = "", **meta) -> Step:
    return Step(command=command, note=note, metadata=meta)


def make_session(name: str, steps=None, **meta) -> Session:
    s = Session(name=name)
    s.metadata.update(meta)
    for step in (steps or []):
        s.steps.append(step)
    return s


@pytest.fixture
def sessions():
    s1 = make_session("deploy", steps=[
        make_step("git pull", note="fetch latest"),
        make_step("docker build .", label="build"),
    ])
    s2 = make_session("cleanup", steps=[
        make_step("rm -rf /tmp/cache", note="clear cache"),
        make_step("git status"),
    ])
    return [s1, s2]


def test_build_index_total(sessions):
    idx = build_index(sessions)
    assert idx.total == 4


def test_build_index_entry_fields(sessions):
    idx = build_index(sessions)
    first = idx.entries[0]
    assert first.command == "git pull"
    assert first.note == "fetch latest"
    assert first.session_name == "deploy"
    assert first.step_index == 0


def test_build_index_step_index_increments(sessions):
    idx = build_index(sessions)
    deploy_entries = [e for e in idx.entries if e.session_name == "deploy"]
    assert deploy_entries[0].step_index == 0
    assert deploy_entries[1].step_index == 1


def test_query_by_command(sessions):
    idx = build_index(sessions)
    results = query_index(idx, command="git")
    assert len(results) == 2
    assert all("git" in e.command for e in results)


def test_query_by_command_case_insensitive(sessions):
    idx = build_index(sessions)
    results = query_index(idx, command="GIT", case_sensitive=False)
    assert len(results) == 2


def test_query_by_command_case_sensitive_no_match(sessions):
    idx = build_index(sessions)
    results = query_index(idx, command="GIT", case_sensitive=True)
    assert len(results) == 0


def test_query_by_note(sessions):
    idx = build_index(sessions)
    results = query_index(idx, note="cache")
    assert len(results) == 1
    assert results[0].command == "rm -rf /tmp/cache"


def test_query_by_session_name(sessions):
    idx = build_index(sessions)
    results = query_index(idx, session_name="deploy")
    assert len(results) == 2


def test_query_combined_filters(sessions):
    idx = build_index(sessions)
    results = query_index(idx, command="git", session_name="deploy")
    assert len(results) == 1
    assert results[0].command == "git pull"


def test_query_no_filters_returns_all(sessions):
    idx = build_index(sessions)
    assert len(query_index(idx)) == 4


def test_format_index_entry_basic():
    entry = IndexEntry(
        session_id="abc",
        session_name="deploy",
        step_index=0,
        command="git pull",
        note="",
    )
    output = format_index_entry(entry)
    assert "deploy" in output
    assert "git pull" in output
    assert "step 1" in output


def test_format_index_entry_with_note():
    entry = IndexEntry(
        session_id="abc",
        session_name="deploy",
        step_index=1,
        command="docker build .",
        note="build image",
    )
    output = format_index_entry(entry)
    assert "build image" in output


def test_build_index_empty():
    idx = build_index([])
    assert idx.total == 0
    assert idx.entries == []
