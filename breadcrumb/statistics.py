from collections import Counter
from datetime import datetime
from typing import List, Optional
from breadcrumb.session import Session, Step


def steps_per_day(session: Session) -> dict:
    """Return a mapping of date string -> step count."""
    counts: Counter = Counter()
    for step in session.steps:
        day = step.timestamp[:10]  # YYYY-MM-DD
        counts[day] += 1
    return dict(sorted(counts.items()))


def average_steps_per_session(sessions: List[Session]) -> float:
    if not sessions:
        return 0.0
    return sum(len(s.steps) for s in sessions) / len(sessions)


def most_active_day(session: Session) -> Optional[str]:
    spd = steps_per_day(session)
    if not spd:
        return None
    return max(spd, key=lambda d: spd[d])


def command_frequency(sessions: List[Session]) -> dict:
    """Aggregate command frequency across multiple sessions."""
    counts: Counter = Counter()
    for session in sessions:
        for step in session.steps:
            cmd = step.command.strip().lower()
            if cmd:
                counts[cmd] += 1
    return dict(counts.most_common())


def session_stats(session: Session) -> dict:
    cmds = [s.command.strip().lower() for s in session.steps if s.command.strip()]
    noted = [s for s in session.steps if s.note]
    return {
        "total_steps": len(session.steps),
        "unique_commands": len(set(cmds)),
        "steps_with_notes": len(noted),
        "most_active_day": most_active_day(session),
        "top_command": Counter(cmds).most_common(1)[0][0] if cmds else None,
    }
