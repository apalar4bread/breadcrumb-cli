from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict
from breadcrumb.session import Session


@dataclass
class TagStats:
    total_tags: int = 0
    unique_tags: int = 0
    tag_counts: Dict[str, int] = field(default_factory=dict)
    sessions_with_tags: int = 0


def compute_tag_stats(sessions: List[Session]) -> TagStats:
    tag_counts: Dict[str, int] = {}
    sessions_with_tags = 0

    for session in sessions:
        session_tags = getattr(session, "tags", []) or []
        if session_tags:
            sessions_with_tags += 1
        for tag in session_tags:
            normalized = tag.lower().strip()
            if normalized:
                tag_counts[normalized] = tag_counts.get(normalized, 0) + 1

    total_tags = sum(tag_counts.values())
    unique_tags = len(tag_counts)

    return TagStats(
        total_tags=total_tags,
        unique_tags=unique_tags,
        tag_counts=tag_counts,
        sessions_with_tags=sessions_with_tags,
    )


def format_tag_stats(stats: TagStats) -> str:
    lines = [
        f"Total tags   : {stats.total_tags}",
        f"Unique tags  : {stats.unique_tags}",
        f"Sessions w/tags: {stats.sessions_with_tags}",
    ]
    if stats.tag_counts:
        lines.append("Tag breakdown:")
        for tag, count in sorted(stats.tag_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {tag}: {count}")
    return "\n".join(lines)
