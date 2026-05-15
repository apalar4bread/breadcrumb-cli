"""Register the plan command with the main CLI."""

from breadcrumb.cli_planner import plan_cmd


def register(cli):
    """Attach plan_cmd to the given Click group."""
    if "plan" not in cli.commands:
        cli.add_command(plan_cmd)
