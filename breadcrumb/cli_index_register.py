"""Register the index command group with the main CLI."""

from breadcrumb.cli_indexer import index_cmd


def register(cli):
    """Attach the index command group to the root CLI."""
    cli.add_command(index_cmd)
