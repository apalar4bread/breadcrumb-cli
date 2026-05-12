import click
from breadcrumb.pinboard_register import register
from breadcrumb.pinboard_cli import pinboard_cmd


def test_register_adds_pinboard_command():
    @click.group()
    def cli():
        pass

    register(cli)
    assert "pinboard" in cli.commands


def test_registered_command_is_pinboard_cmd():
    @click.group()
    def cli():
        pass

    register(cli)
    assert cli.commands["pinboard"] is pinboard_cmd


def test_register_does_not_duplicate():
    @click.group()
    def cli():
        pass

    register(cli)
    register(cli)
    assert list(cli.commands.keys()).count("pinboard") == 1
