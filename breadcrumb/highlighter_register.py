"""Register the highlighter CLI command with the main CLI group."""

from breadcrumb.highlighter_cli import highlight_cmd


def register(cli):
    """Attach highlight_cmd to the given Click group if not already present."""
    if "highlight" not in cli.commands:
        cli.add_command(highlight_cmd, name="highlight")
