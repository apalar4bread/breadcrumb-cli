"""Diff two sessions to show what changed between them."""

from typing import List, Tuple
from breadcrumb.session import Session, Step


def diff_sessions(session_a: Session, session_b: Session) -> List[dict]:
    """Compare two sessions step by step and return diff entries."""
    steps_a = session_a.steps
    steps_b = session_b.steps
    max_len = max(len(steps_a), len(steps_b))
    diffs = []

    for i in range(max_len):
        if i >= len(steps_a):
            diffs.append({"index": i, "status": "added", "step": steps_b[i]})
        elif i >= len(steps_b):
            diffs.append({"index": i, "status": "removed", "step": steps_a[i]})
        elif steps_a[i].command != steps_b[i].command:
            diffs.append({
                "index": i,
                "status": "changed",
                "old": steps_a[i],
                "new": steps_b[i],
            })
        else:
            diffs.append({"index": i, "status": "same", "step": steps_a[i]})

    return diffs


def format_diff(diffs: List[dict]) -> str:
    """Render diff entries as a human-readable string."""
    lines = []
    for entry in diffs:
        idx = entry["index"]
        status = entry["status"]
        if status == "same":
            lines.append(f"  [{idx}] {entry['step'].command}")
        elif status == "added":
            lines.append(f"+ [{idx}] {entry['step'].command}")
        elif status == "removed":
            lines.append(f"- [{idx}] {entry['step'].command}")
        elif status == "changed":
            lines.append(f"- [{idx}] {entry['old'].command}")
            lines.append(f"+ [{idx}] {entry['new'].command}")
    return "\n".join(lines)


def sessions_are_identical(diffs: List[dict]) -> bool:
    return all(d["status"] == "same" for d in diffs)
