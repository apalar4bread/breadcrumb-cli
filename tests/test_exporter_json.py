"""Tests for breadcrumb.exporter_json."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from breadcrumb.exporter_json import JsonExportError, export_to_json, write_json
from breadcrumb.session import Session, add_step


def make_session(name: str = "mysession") -> Session:
    s = Session(id="abc123", name=name, created_at="2024-01-01T00:00:00", steps=[], tags=set(), metadata={})
    add_step(s, command="echo hello", note="greet")
    add_step(s, command="ls -la")
    return s


def test_export_returns_valid_json():
    s = make_session()
    raw = export_to_json(s)
    data = json.loads(raw)
    assert isinstance(data, dict)


def test_export_contains_session_name():
    s = make_session(name="demo")
    data = json.loads(export_to_json(s))
    assert data["name"] == "demo"


def test_export_step_count():
    s = make_session()
    data = json.loads(export_to_json(s))
    assert len(data["steps"]) == 2


def test_export_step_command():
    s = make_session()
    data = json.loads(export_to_json(s))
    commands = [step["command"] for step in data["steps"]]
    assert "echo hello" in commands


def test_export_step_note():
    s = make_session()
    data = json.loads(export_to_json(s))
    assert data["steps"][0]["note"] == "greet"


def test_export_step_index_starts_at_one():
    s = make_session()
    data = json.loads(export_to_json(s))
    assert data["steps"][0]["index"] == 1


def test_export_empty_session():
    s = Session(id="x", name="empty", created_at="2024-01-01", steps=[], tags=set(), metadata={})
    data = json.loads(export_to_json(s))
    assert data["steps"] == []


def test_write_json_creates_file(tmp_path: Path):
    s = make_session()
    dest = tmp_path / "out.json"
    result = write_json(s, dest)
    assert result == dest
    assert dest.exists()


def test_write_json_content_is_valid(tmp_path: Path):
    s = make_session()
    dest = tmp_path / "out.json"
    write_json(s, dest)
    data = json.loads(dest.read_text())
    assert data["id"] == "abc123"


def test_write_json_wrong_extension_raises(tmp_path: Path):
    s = make_session()
    with pytest.raises(JsonExportError):
        write_json(s, tmp_path / "out.txt")
