"""Compute statistics about tag usage across sessions."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from breadcrumb.session import Session


@dataclass
class TagStats:
    total_tags: int
    unique_tags: int
    tag_counts: Dict[str, int]
    most_common: List[tuple]
    sessions_with_tags: int
    sessions_without_tags: int


def compute_tag_stats(sessions: List[Session]) -> TagStats:
    """Compute tag usage statistics across a list of sessions."""
    if not sessions:
        return TagStats(
            total_tags=0,
            unique_tags=0,
            tag_counts={},
            most_common=[],
            sessions_with_tags=0,
            sessions_without_tags=0,
        )

    counter: Counter = Counter()
    sessions_with_tags = 0
    sessions_without_tags = 0

    for session in sessions:
        tags = session.metadata.get("tags", [])
        if isinstance(tags, list) and tags:
            sessions_with_tags += 1
            for tag in tags:
                counter[tag.lower()] += 1
        else:
            sessions_without_tags += 1

    tag_counts = dict(counter)
    total_tags = sum(counter.values())
    unique_tags = len(counter)
    most_common = counter.most_common(5)

    return TagStats(
        total_tags=total_tags,
        unique_tags=unique_tags,
        tag_counts=tag_counts,
        most_common=most_common,
        sessions_with_tags=sessions_with_tags,
        sessions_without_tags=sessions_without_tags,
    )


def format_tag_stats(stats: TagStats) -> str:
    """Format tag statistics into a human-readable string."""
    lines = [
        f"Total tag usages : {stats.total_tags}",
        f"Unique tags      : {stats.unique_tags}",
        f"Tagged sessions  : {stats.sessions_with_tags}",
        f"Untagged sessions: {stats.sessions_without_tags}",
    ]
    if stats.most_common:
        lines.append("Top tags:")
        for tag, count in stats.most_common:
            lines.append(f"  {tag}: {count}")
    return "\n".join(lines)
