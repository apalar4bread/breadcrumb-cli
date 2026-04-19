"""Tests for breadcrumb.exporter_html."""
from __future__ import annotations

import pytest
from pathlib import Path
from breadcrumb.session import Session, add_step
from breadcrumb.exporter_html import export_to_html, write_html


def make_session(name="demo") -> Session:
    s = Session(id="s1", name=name, steps=[], tags=["ci"])
    add_step(s, "git status")
    add_step(s, "pytest tests/", note="run tests")
    return s


def test_export_returns_string():
    s = make_session()
    html = export_to_html(s)
    assert isinstance(html, str)


def test_export_contains_session_name():
    s = make_session("my-session")
    html = export_to_html(s)
    assert "my-session" in html


def test_export_contains_commands():
    s = make_session()
    html = export_to_html(s)
    assert "git status" in html
    assert "pytest tests/" in html


def test_export_contains_note():
    s = make_session()
    html = export_to_html(s)
    assert "run tests" in html


def test_export_contains_tag():
    s = make_session()
    html = export_to_html(s)
    assert "ci" in html


def test_export_empty_session():
    s = Session(id="s2", name="empty", steps=[], tags=[])
    html = export_to_html(s)
    assert "No steps recorded" in html


def test_export_step_count_shown():
    s = make_session()
    html = export_to_html(s)
    assert f"Steps ({len(s.steps)})" in html


def test_write_html_creates_file(tmp_path):
    s = make_session()
    out = tmp_path / "out.html"
    result = write_html(s, str(out))
    assert result.exists()
    assert result.read_text(encoding="utf-8").startswith("<!DOCTYPE html>")


def test_write_html_wrong_extension_raises(tmp_path):
    s = make_session()
    with pytest.raises(ValueError, match=".html"):
        write_html(s, str(tmp_path / "out.txt"))


def test_export_valid_html_structure():
    s = make_session()
    html = export_to_html(s)
    assert "<html" in html
    assert "</html>" in html
    assert "<body>" in html
    assert "</body>" in html
