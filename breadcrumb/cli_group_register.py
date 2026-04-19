"""Register group_cmd into the main CLI."""
from breadcrumb.cli import cli
from breadcrumb.cli_group import group_cmd


def register():
    cli.add_command(group_cmd)


if __name__ == "__main__":
    register()
    cli()
