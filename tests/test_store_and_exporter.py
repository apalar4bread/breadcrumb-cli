"""Tests for SessionStore persistence and script exporter."""

import os
import tempfile
from pathlib import Path
import pytest

from breadcrumb.session import Session
from breadcrumb.store import SessionStore
from breadcrumb.exporter import export_to_script, write_script


@pytest.fixture
def tmp_store(tmp_path):
    return SessionStore(store_dir=tmp_path)


def make_session(name="demo"):
    s = Session(name=name)
    s.add_step("echo start", cwd="/tmp", exit_code=0, note="begin")
    s.add_step("mkdir -p build", cwd="/tmp", exit_code=0)
    return s


def test_save_and_load(tmp_store):
    s = make_session()
    tmp_store.save(s)
    loaded = tmp_store.load("demo")
    assert loaded.name == "demo"
    assert len(loaded.steps) == 2
    assert loaded.steps[0].command == "echo start"


def test_list_sessions(tmp_store):
    tmp_store.save(make_session("alpha"))
    tmp_store.save(make_session("beta"))
    names = tmp_store.list_sessions()
    assert "alpha" in names
    assert "beta" in names


def test_delete_session(tmp_store):
    tmp_store.save(make_session("todelete"))
    tmp_store.delete("todelete")
    assert not tmp_store.exists("todelete")


def test_load_missing_raises(tmp_store):
    with pytest.raises(FileNotFoundError):
        tmp_store.load("ghost")


def test_export_script_contains_commands():
    s = make_session()
    script = export_to_script(s)
    assert "echo start" in script
    assert "mkdir -p build" in script
    assert "#!/usr/bin/env bash" in script


def test_export_includes_notes():
    s = make_session()
    script = export_to_script(s, include_notes=True)
    assert "# begin" in script


def test_write_script_is_executable(tmp_path):
    s = make_session()
    out = str(tmp_path / "run.sh")
    write_script(s, out)
    assert os.access(out, os.X_OK)
