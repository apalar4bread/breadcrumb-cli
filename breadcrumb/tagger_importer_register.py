"""Register tag-import CLI command with the main CLI group."""

from breadcrumb.cli_tagger_importer import tag_import_cmd


def register(cli):
    """Attach tag-import command group to the given Click CLI."""
    if "tag-import" not in cli.commands:
        cli.add_command(tag_import_cmd)
