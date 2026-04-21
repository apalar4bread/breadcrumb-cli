from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from breadcrumb.session import Session, Step
from breadcrumb.cli_chunker import chunk_cmd


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="demo", n=6):
    s = Session(name=name)
    for i in range(n):
        s.steps.append(Step(command=f"cmd_{i}"))
    return s


@pytest.fixture
def mock_store(monkeypatch):
    store = MagicMock()
    monkeypatch.setattr("breadcrumb.cli_chunker._get_store", lambda: store)
    return store


def invoke(runner, *args):
    return runner.invoke(chunk_cmd, list(args))


# --- show ---

def test_show_chunks_output(runner, mock_store):
    mock_store.load.return_value = make_session(n=6)
    result = invoke(runner, "show", "demo", "--size", "2")
    assert result.exit_code == 0
    assert "Total chunks: 3" in result.output


def test_show_chunks_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "show", "missing")
    assert result.exit_code != 0
    assert "not found" in result.output


def test_show_chunks_invalid_size(runner, mock_store):
    mock_store.load.return_value = make_session(n=3)
    result = invoke(runner, "show", "demo", "--size", "0")
    assert result.exit_code != 0
    assert "Error" in result.output


# --- split ---

def test_split_chunks_lists_names(runner, mock_store):
    mock_store.load.return_value = make_session(n=4)
    result = invoke(runner, "split", "demo", "--size", "2")
    assert result.exit_code == 0
    assert "chunk 1" in result.output
    assert "chunk 2" in result.output


def test_split_chunks_save_flag_calls_store(runner, mock_store):
    mock_store.load.return_value = make_session(n=4)
    result = invoke(runner, "split", "demo", "--size", "2", "--save")
    assert result.exit_code == 0
    assert mock_store.save.call_count == 2
    assert "Saved 2" in result.output


def test_split_chunks_no_save_hint(runner, mock_store):
    mock_store.load.return_value = make_session(n=3)
    result = invoke(runner, "split", "demo", "--size", "2")
    assert result.exit_code == 0
    assert "--save" in result.output


def test_split_session_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = invoke(runner, "split", "ghost")
    assert result.exit_code != 0
    assert "not found" in result.output
