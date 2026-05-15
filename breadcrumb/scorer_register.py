from breadcrumb.scorer_cli import score_cmd


def register(cli):
    """Register the score command group with the root CLI."""
    cli.add_command(score_cmd)
