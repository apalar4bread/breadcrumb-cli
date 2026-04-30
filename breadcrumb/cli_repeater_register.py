"""Register repeater commands with the main CLI."""

from breadcrumb.cli_repeater import repeat_cmd


def register(cli):
    """Attach the repeat command group to *cli*."""
    cli.add_command(repeat_cmd)
