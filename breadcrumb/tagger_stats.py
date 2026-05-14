from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter
from typing import List, Dict

from breadcrumb.session import Session


@dataclass
class TagStats:
    total_tags: int = 0
    unique_tags: int = 0
    tag_counts: Dict[str, int] = field(default_factory=dict)
    most_common: List[tuple] = field(default_factory=list)
    sessions_with_tags: int = 0
    sessions_without_tags: int = 0


def compute_tag_stats(sessions: List[Session]) -> TagStats:
    counter: Counter = Counter()
    sessions_with = 0
    sessions_without = 0

    for session in sessions:
        tags = getattr(session, "tags", []) or []
        if tags:
            sessions_with += 1
            for tag in tags:
                counter[tag.lower()] += 1
        else:
            sessions_without += 1

    return TagStats(
        total_tags=sum(counter.values()),
        unique_tags=len(counter),
        tag_counts=dict(counter),
        most_common=counter.most_common(5),
        sessions_with_tags=sessions_with,
        sessions_without_tags=sessions_without,
    )


def format_tag_stats(stats: TagStats) -> str:
    lines = [
        f"Total tag usages : {stats.total_tags}",
        f"Unique tags      : {stats.unique_tags}",
        f"Sessions w/ tags : {stats.sessions_with_tags}",
        f"Sessions w/o tags: {stats.sessions_without_tags}",
    ]
    if stats.most_common:
        lines.append("Top tags:")
        for tag, count in stats.most_common:
            lines.append(f"  {tag}: {count}")
    return "\n".join(lines)
