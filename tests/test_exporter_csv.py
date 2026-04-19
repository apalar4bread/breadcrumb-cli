"""Tests for CSV exporter."""
import csv
import io
import pytest
from pathlib import Path
from breadcrumb.session import Session, Step
from breadcrumb.exporter_csv import export_to_csv, write_csv


def make_session(name="test", steps=None):
    s = Session(name=name)
    for cmd, note in (steps or []):
        s.steps.append(Step(command=cmd, note=note))
    return s


def parse_csv(text):
    return list(csv.DictReader(io.StringIO(text)))


def test_export_empty_session():
    s = make_session()
    rows = parse_csv(export_to_csv(s))
    assert rows == []


def test_export_step_count():
    s = make_session(steps=[("ls", None), ("pwd", "where am i")])
    rows = parse_csv(export_to_csv(s))
    assert len(rows) == 2


def test_export_step_numbers():
    s = make_session(steps=[("ls", None), ("pwd", None)])
    rows = parse_csv(export_to_csv(s))
    assert rows[0]["step"] == "1"
    assert rows[1]["step"] == "2"


def test_export_command_and_note():
    s = make_session(steps=[("echo hello", "greet")])
    rows = parse_csv(export_to_csv(s))
    assert rows[0]["command"] == "echo hello"
    assert rows[0]["note"] == "greet"


def test_export_note_empty_when_none():
    s = make_session(steps=[("ls", None)])
    rows = parse_csv(export_to_csv(s))
    assert rows[0]["note"] == ""


def test_export_pinned_flag():
    s = make_session(steps=[("ls", None)])
    s.steps[0].metadata["pinned"] = True
    rows = parse_csv(export_to_csv(s))
    assert rows[0]["pinned"] == "yes"


def test_export_not_pinned_flag():
    s = make_session(steps=[("ls", None)])
    rows = parse_csv(export_to_csv(s))
    assert rows[0]["pinned"] == "no"


def test_export_tags_pipe_separated():
    s = make_session(steps=[("ls", None)])
    s.steps[0].metadata["tags"] = ["alpha", "beta"]
    rows = parse_csv(export_to_csv(s))
    assert rows[0]["tags"] == "alpha|beta"


def test_write_csv_creates_file(tmp_path):
    s = make_session(steps=[("ls", None)])
    out = tmp_path / "out.csv"
    result = write_csv(s, str(out))
    assert result == out
    assert out.exists()


def test_write_csv_wrong_extension_raises(tmp_path):
    s = make_session(steps=[("ls", None)])
    with pytest.raises(ValueError, match=".csv"):
        write_csv(s, str(tmp_path / "out.txt"))
