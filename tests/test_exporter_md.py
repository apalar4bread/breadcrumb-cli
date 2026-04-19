"""Tests for Markdown exporter."""
import pytest
from breadcrumb.session import Session, add_step
from breadcrumb.exporter_md import export_to_markdown, write_markdown


def make_session(name="demo") -> Session:
    s = Session(name=name)
    return s


def test_export_empty_session():
    s = make_session()
    md = export_to_markdown(s)
    assert "# demo" in md
    assert "_No steps recorded._" in md


def test_export_heading_contains_name():
    s = make_session("my-session")
    md = export_to_markdown(s)
    assert md.startswith("# my-session")


def test_export_step_command_in_code_block():
    s = make_session()
    add_step(s, "echo hello")
    md = export_to_markdown(s)
    assert "```sh" in md
    assert "echo hello" in md


def test_export_step_with_note():
    s = make_session()
    add_step(s, "ls -la", note="list files")
    md = export_to_markdown(s)
    assert "list files" in md
    assert "### Step 1 — list files" in md


def test_export_tags_shown():
    s = make_session()
    s.tags = ["deploy", "prod"]
    md = export_to_markdown(s)
    assert "`deploy`" in md
    assert "`prod`" in md


def test_export_verbose_shows_metadata():
    s = make_session()
    add_step(s, "git push", metadata={"env": "production"})
    md = export_to_markdown(s, verbose=True)
    assert "`env`" in md
    assert "production" in md


def test_export_no_verbose_hides_metadata():
    s = make_session()
    add_step(s, "git push", metadata={"env": "production"})
    md = export_to_markdown(s, verbose=False)
    assert "`env`" not in md


def test_export_multiple_steps_numbered():
    s = make_session()
    add_step(s, "step one")
    add_step(s, "step two")
    md = export_to_markdown(s)
    assert "### Step 1" in md
    assert "### Step 2" in md


def test_write_markdown_creates_file(tmp_path):
    s = make_session("write-test")
    add_step(s, "echo hi")
    out = tmp_path / "out.md"
    write_markdown(s, str(out))
    content = out.read_text()
    assert "# write-test" in content
    assert "echo hi" in content
