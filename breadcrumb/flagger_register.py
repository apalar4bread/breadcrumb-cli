"""Register the flag command group with the root CLI."""
from breadcrumb.cli_flagger import flag_cmd


def register(cli):
    """Attach flag_cmd to *cli* if not already present."""
    if "flag" not in cli.commands:
        cli.add_command(flag_cmd)
