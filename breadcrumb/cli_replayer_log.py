"""CLI commands for viewing and managing replay logs."""

from __future__ import annotations

import json
from pathlib import Path

import click

from breadcrumb.replayer_log import ReplayLog, format_log


def _log_path(session_id: str, log_dir: Path) -> Path:
    return log_dir / f"{session_id}.replay.json"


@click.group("replay-log")
def replay_log_cmd() -> None:
    """View and manage replay execution logs."""


@replay_log_cmd.command("show")
@click.argument("session_id")
@click.option("--log-dir", default=".breadcrumb/logs", show_default=True, help="Directory containing replay logs.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output raw JSON.")
def show_log(session_id: str, log_dir: str, as_json: bool) -> None:
    """Show the replay log for SESSION_ID."""
    path = _log_path(session_id, Path(log_dir))
    if not path.exists():
        raise click.ClickException(f"No replay log found for session '{session_id}'.")

    data = json.loads(path.read_text())
    log = ReplayLog.from_dict(data)

    if as_json:
        click.echo(json.dumps(log.to_dict(), indent=2))
    else:
        click.echo(format_log(log))


@replay_log_cmd.command("list")
@click.option("--log-dir", default=".breadcrumb/logs", show_default=True, help="Directory containing replay logs.")
def list_logs(log_dir: str) -> None:
    """List all available replay logs."""
    base = Path(log_dir)
    if not base.exists():
        click.echo("No replay logs found.")
        return

    logs = sorted(base.glob("*.replay.json"))
    if not logs:
        click.echo("No replay logs found.")
        return

    for log_file in logs:
        data = json.loads(log_file.read_text())
        log = ReplayLog.from_dict(data)
        status = "done" if log.finished_at else "incomplete"
        click.echo(
            f"  {log.session_id[:8]}  {log.session_name:<30}  "
            f"ok={log.success_count} fail={log.failure_count} skip={log.skipped_count}  [{status}]"
        )


@replay_log_cmd.command("delete")
@click.argument("session_id")
@click.option("--log-dir", default=".breadcrumb/logs", show_default=True)
@click.confirmation_option(prompt="Delete this replay log?")
def delete_log(session_id: str, log_dir: str) -> None:
    """Delete the replay log for SESSION_ID."""
    path = _log_path(session_id, Path(log_dir))
    if not path.exists():
        raise click.ClickException(f"No replay log found for session '{session_id}'.")
    path.unlink()
    click.echo(f"Deleted replay log for '{session_id}'.")
