from breadcrumb.tagger_cli import tag_cmd


def register(cli):
    """Register the tag command group with the main CLI."""
    cli.add_command(tag_cmd)
