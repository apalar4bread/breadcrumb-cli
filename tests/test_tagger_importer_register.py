"""Tests for tagger_importer_register."""

import click
import pytest

from breadcrumb.tagger_importer_register import register
from breadcrumb.cli_tagger_importer import tag_import_cmd


@pytest.fixture
def cli():
    @click.group()
    def _cli():
        pass
    return _cli


def test_register_adds_tag_import_command(cli):
    register(cli)
    assert "tag-import" in cli.commands


def test_registered_command_is_tag_import_cmd(cli):
    register(cli)
    assert cli.commands["tag-import"] is tag_import_cmd


def test_register_does_not_duplicate(cli):
    register(cli)
    register(cli)
    names = [name for name in cli.commands if name == "tag-import"]
    assert len(names) == 1


def test_tag_import_has_add_subcommand(cli):
    register(cli)
    cmd = cli.commands["tag-import"]
    assert "add" in cmd.commands


def test_tag_import_has_from_text_subcommand(cli):
    register(cli)
    cmd = cli.commands["tag-import"]
    assert "from-text" in cmd.commands
