from breadcrumb.splitter_cli import split_cmd


def register(cli):
    """Register the split command group with the root CLI."""
    if "split" not in cli.commands:
        cli.add_command(split_cmd)
