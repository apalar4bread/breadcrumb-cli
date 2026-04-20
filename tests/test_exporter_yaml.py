"""Tests for YAML exporter."""

import pytest
from unittest.mock import patch, MagicMock

pyaml = pytest.importorskip("yaml")

from breadcrumb.session import Session
from breadcrumb.exporter_yaml import export_to_yaml, write_yaml, YamlExportError


def make_session(name="demo", commands=None):
    s = Session(name=name)
    for cmd in (commands or ["echo hello", "ls -la"]):
        s.add_step(cmd)
    return s


def test_export_returns_string():
    s = make_session()
    result = export_to_yaml(s)
    assert isinstance(result, str)


def test_export_contains_session_name():
    s = make_session(name="my-session")
    result = export_to_yaml(s)
    assert "my-session" in result


def test_export_contains_commands():
    s = make_session(commands=["git status", "git diff"])
    result = export_to_yaml(s)
    assert "git status" in result
    assert "git diff" in result


def test_export_step_count():
    s = make_session(commands=["a", "b", "c"])
    data = pyaml.safe_load(export_to_yaml(s))
    assert len(data["session"]["steps"]) == 3


def test_export_step_index_starts_at_one():
    s = make_session(commands=["only"])
    data = pyaml.safe_load(export_to_yaml(s))
    assert data["session"]["steps"][0]["index"] == 1


def test_export_step_with_note():
    s = make_session(commands=[])
    s.add_step("make build", note="builds the project")
    data = pyaml.safe_load(export_to_yaml(s))
    assert data["session"]["steps"][0]["note"] == "builds the project"


def test_export_tags_included():
    s = make_session()
    s.tags.add("ci")
    data = pyaml.safe_load(export_to_yaml(s))
    assert "ci" in data["session"]["tags"]


def test_export_empty_steps():
    s = Session(name="empty")
    data = pyaml.safe_load(export_to_yaml(s))
    assert data["session"]["steps"] == []


def test_write_yaml_wrong_extension_raises(tmp_path):
    s = make_session()
    bad_path = str(tmp_path / "output.txt")
    with pytest.raises(YamlExportError, match="extension"):
        write_yaml(s, bad_path)


def test_write_yaml_creates_file(tmp_path):
    s = make_session(name="file-test")
    out = tmp_path / "session.yaml"
    result = write_yaml(s, str(out))
    assert result.exists()
    content = out.read_text()
    assert "file-test" in content


def test_write_yaml_accepts_yml_extension(tmp_path):
    s = make_session()
    out = tmp_path / "session.yml"
    result = write_yaml(s, str(out))
    assert result.exists()


def test_export_raises_without_pyyaml():
    import breadcrumb.exporter_yaml as mod
    original = mod.yaml
    mod.yaml = None
    try:
        with pytest.raises(YamlExportError, match="PyYAML"):
            export_to_yaml(make_session())
    finally:
        mod.yaml = original
