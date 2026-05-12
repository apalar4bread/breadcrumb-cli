import pytest
import click
from breadcrumb.tagger_register import register
from breadcrumb.tagger_cli import tag_cmd


@click.group()
def cli():
    pass


def test_register_adds_tag_command():
    @click.group()
    def cli():
        pass

    register(cli)
    assert "tag" in cli.commands


def test_registered_command_is_tag_cmd():
    @click.group()
    def cli():
        pass

    register(cli)
    assert cli.commands["tag"] is tag_cmd


def test_register_does_not_duplicate():
    @click.group()
    def cli():
        pass

    register(cli)
    register(cli)
    # Should still only have one 'tag' entry
    assert list(cli.commands.keys()).count("tag") == 1
