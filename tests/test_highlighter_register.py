"""Tests for highlighter_register.register()."""

import click
import pytest
from click.testing import CliRunner

from breadcrumb.highlighter_register import register
from breadcrumb.highlighter_cli import highlight_cmd


@pytest.fixture()
def cli():
    @click.group()
    def _cli():
        pass

    return _cli


def test_register_adds_highlight_command(cli):
    register(cli)
    assert "highlight" in cli.commands


def test_registered_command_is_highlight_cmd(cli):
    register(cli)
    assert cli.commands["highlight"] is highlight_cmd


def test_register_does_not_duplicate(cli):
    register(cli)
    register(cli)
    names = [name for name in cli.commands if name == "highlight"]
    assert len(names) == 1


def test_register_does_not_affect_other_commands(cli):
    @cli.command()
    def other():
        pass

    register(cli)
    assert "other" in cli.commands
    assert "highlight" in cli.commands
    assert len(cli.commands) == 2
