"""Badge system: award badges to sessions based on activity milestones."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session

BADGE_RULES = {
    "first_step": "Awarded when a session has at least 1 step.",
    "five_steps": "Awarded when a session has at least 5 steps.",
    "ten_steps": "Awarded when a session has at least 10 steps.",
    "tagged": "Awarded when a session has at least one tag.",
    "noted": "Awarded when every step has a note.",
    "pinned": "Awarded when at least one step is pinned.",
    "bookmarked": "Awarded when at least one step is bookmarked.",
}


class BadgeError(Exception):
    pass


@dataclass
class BadgeResult:
    session_id: str
    session_name: str
    badges: List[str] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.badges)

    def summary(self) -> str:
        if not self.badges:
            return f"'{self.session_name}' earned no badges."
        names = ", ".join(self.badges)
        return f"'{self.session_name}' earned {self.count} badge(s): {names}"


def award_badges(session: Session) -> BadgeResult:
    """Evaluate a session and return all earned badges."""
    if not session.id:
        raise BadgeError("Session must have an id.")

    result = BadgeResult(session_id=session.id, session_name=session.name)
    steps = session.steps

    if len(steps) >= 1:
        result.badges.append("first_step")
    if len(steps) >= 5:
        result.badges.append("five_steps")
    if len(steps) >= 10:
        result.badges.append("ten_steps")
    if session.tags:
        result.badges.append("tagged")
    if steps and all(s.note and s.note.strip() for s in steps):
        result.badges.append("noted")
    if any(s.metadata.get("pinned") for s in steps):
        result.badges.append("pinned")
    if any(s.metadata.get("bookmarked") for s in steps):
        result.badges.append("bookmarked")

    return result


def format_badge_result(result: BadgeResult) -> str:
    lines = [f"Badges for '{result.session_name}':", ""]
    if not result.badges:
        lines.append("  (none)")
    else:
        for badge in result.badges:
            desc = BADGE_RULES.get(badge, "")
            lines.append(f"  [{badge}] {desc}")
    return "\n".join(lines)
