"""Tests for breadcrumb.cli_digester."""

from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from breadcrumb.cli_digester import digest_cmd
from breadcrumb.session import Session, add_step


@pytest.fixture
def runner():
    return CliRunner()


def make_session(name="s", commands=None):
    s = Session(name=name)
    for cmd in (commands or []):
        add_step(s, cmd)
    return s


@pytest.fixture
def mock_store():
    with patch("breadcrumb.cli_digester._get_store") as p:
        store = MagicMock()
        p.return_value = store
        yield store


def invoke(runner, *args):
    return runner.invoke(digest_cmd, list(args), catch_exceptions=False)


def test_show_digest_output(runner, mock_store):
    s = make_session("demo", ["ls", "pwd"])
    mock_store.load.return_value = s
    result = invoke(runner, "show", s.id)
    assert result.exit_code == 0
    assert "demo" in result.output
    assert "Fingerprint" in result.output


def test_show_digest_not_found(runner, mock_store):
    mock_store.load.return_value = None
    result = runner.invoke(digest_cmd, ["show", "missing-id"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_compare_identical(runner, mock_store):
    s1 = make_session("a", ["ls", "pwd"])
    s2 = make_session("b", ["ls", "pwd"])
    mock_store.load.side_effect = [s1, s2]
    result = invoke(runner, "compare", s1.id, s2.id)
    assert result.exit_code == 0
    assert "IDENTICAL" in result.output


def test_compare_different(runner, mock_store):
    s1 = make_session("a", ["ls"])
    s2 = make_session("b", ["pwd"])
    mock_store.load.side_effect = [s1, s2]
    result = invoke(runner, "compare", s1.id, s2.id)
    assert result.exit_code == 0
    assert "DIFFERENT" in result.output


def test_compare_first_not_found(runner, mock_store):
    mock_store.load.side_effect = [None, make_session()]
    result = runner.invoke(digest_cmd, ["compare", "x", "y"])
    assert result.exit_code != 0


def test_compare_second_not_found(runner, mock_store):
    mock_store.load.side_effect = [make_session(), None]
    result = runner.invoke(digest_cmd, ["compare", "x", "y"])
    assert result.exit_code != 0
