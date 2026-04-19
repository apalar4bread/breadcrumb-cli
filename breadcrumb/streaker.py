"""Track consecutive-day usage streaks for sessions."""
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import List
from breadcrumb.session import Session


class StreakerError(Exception):
    pass


@dataclass
class StreakResult:
    current_streak: int = 0
    longest_streak: int = 0
    active_days: List[str] = field(default_factory=list)
    last_active: str = ""


def _day_str(ts: str) -> str:
    """Return YYYY-MM-DD from an ISO timestamp string."""
    return ts[:10]


def compute_streak(sessions: List[Session]) -> StreakResult:
    """Compute activity streaks across all sessions."""
    days = set()
    for s in sessions:
        for step in s.steps:
            days.add(_day_str(step.timestamp))

    if not days:
        return StreakResult()

    sorted_days = sorted(days)
    result = StreakResult(active_days=sorted_days, last_active=sorted_days[-1])

    # compute longest streak
    best = cur = 1
    for i in range(1, len(sorted_days)):
        prev = datetime.fromisoformat(sorted_days[i - 1])
        curr = datetime.fromisoformat(sorted_days[i])
        if (curr - prev).days == 1:
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    result.longest_streak = best

    # compute current streak (from today backwards)
    today = datetime.now(timezone.utc).date()
    streak = 0
    check = today
    day_set = set(sorted_days)
    while str(check) in day_set:
        streak += 1
        check -= timedelta(days=1)
    result.current_streak = streak

    return result


def format_streak(result: StreakResult) -> str:
    lines = [
        f"Current streak : {result.current_streak} day(s)",
        f"Longest streak : {result.longest_streak} day(s)",
        f"Total active days: {len(result.active_days)}",
        f"Last active    : {result.last_active or 'never'}",
    ]
    return "\n".join(lines)
