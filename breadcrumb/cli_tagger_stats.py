import click
from breadcrumb.store import SessionStore
from breadcrumb.tagger_stats import compute_tag_stats, format_tag_stats


def _get_store() -> SessionStore:
    return SessionStore()


@click.group("tag-stats")
def tag_stats_cmd():
    """Show statistics about tags across sessions."""


@tag_stats_cmd.command("show")
@click.option("--top", default=0, help="Show only the top N tags by frequency.")
def show_stats(top: int):
    """Display tag usage statistics."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    stats = compute_tag_stats(sessions)

    if top > 0 and stats.tag_counts:
        trimmed = dict(
            sorted(stats.tag_counts.items(), key=lambda x: -x[1])[:top]
        )
        from breadcrumb.tagger_stats import TagStats
        stats = TagStats(
            total_tags=sum(trimmed.values()),
            unique_tags=len(trimmed),
            tag_counts=trimmed,
            sessions_with_tags=stats.sessions_with_tags,
        )

    click.echo(format_tag_stats(stats))


@tag_stats_cmd.command("top")
@click.argument("n", type=int, default=5)
def top_tags(n: int):
    """List the top N most-used tags."""
    store = _get_store()
    sessions = [store.load(sid) for sid in store.list_sessions()]
    stats = compute_tag_stats(sessions)

    ranked = sorted(stats.tag_counts.items(), key=lambda x: -x[1])[:n]
    if not ranked:
        click.echo("No tags found.")
        return
    for tag, count in ranked:
        click.echo(f"{tag}: {count}")
