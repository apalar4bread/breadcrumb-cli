from breadcrumb.tagger_cli import tag_cmd


def register(cli):
    """Register the tag command group with the main CLI."""
    if "tag" not in cli.commands:
        cli.add_command(tag_cmd)
