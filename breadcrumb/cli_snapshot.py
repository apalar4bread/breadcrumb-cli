"""CLI commands for snapshots."""
import click
from breadcrumb.store import SessionStore
from breadcrumb.snapshot_store import SnapshotStore
from breadcrumb.snapshotter import take_snapshot, restore_snapshot, SnapshotError


@click.group("snapshot")
def snapshot_cmd():
    """Manage session snapshots."""


def _stores(ctx):
    store: SessionStore = ctx.obj["store"]
    snap_store = SnapshotStore(store.base_dir / "snapshots")
    return store, snap_store


@snapshot_cmd.command("take")
@click.argument("session_id")
@click.argument("label")
@click.option("--up-to", type=int, default=None, help="Step index (0-based) to snapshot up to.")
@click.pass_context
def take_cmd(ctx, session_id, label, up_to):
    """Take a snapshot of SESSION_ID labelled LABEL."""
    store, snap_store = _stores(ctx)
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        snap = take_snapshot(session, up_to=up_to)
    except SnapshotError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)
    snap_store.save(snap, label)
    click.echo(f"Snapshot '{label}' saved ({len(snap.steps)} steps).")


@snapshot_cmd.command("list")
@click.argument("session_id")
@click.pass_context
def list_cmd(ctx, session_id):
    """List snapshots for SESSION_ID."""
    _, snap_store = _stores(ctx)
    labels = snap_store.list_snapshots(session_id)
    if not labels:
        click.echo("No snapshots found.")
    for label in labels:
        click.echo(f"  {label}")


@snapshot_cmd.command("restore")
@click.argument("session_id")
@click.argument("label")
@click.pass_context
def restore_cmd(ctx, session_id, label):
    """Restore SESSION_ID to snapshot LABEL."""
    store, snap_store = _stores(ctx)
    session = store.load(session_id)
    if session is None:
        click.echo(f"Session '{session_id}' not found.", err=True)
        raise SystemExit(1)
    try:
        snap = snap_store.load(session_id, label)
    except FileNotFoundError as e:
        click.echo(str(e), err=True)
        raise SystemExit(1)
    restored = restore_snapshot(snap, session)
    store.save(restored)
    click.echo(f"Session restored to snapshot '{label}' ({len(restored.steps)} steps).")
