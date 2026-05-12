from breadcrumb.pinboard_cli import pinboard_cmd


def register(cli):
    cli.add_command(pinboard_cmd)
