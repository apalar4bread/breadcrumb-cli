"""Profile sessions by timing and command patterns."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from breadcrumb.session import Session, Step


@dataclass
class ProfileResult:
    session_id: str
    session_name: str
    total_steps: int
    unique_commands: int
    top_commands: List[tuple]
    first_step_time: Optional[str]
    last_step_time: Optional[str]
    duration_seconds: Optional[float]
    has_notes: int
    has_tags: bool


def profile_session(session: Session) -> ProfileResult:
    steps = session.steps
    if not steps:
        return ProfileResult(
            session_id=session.id,
            session_name=session.name,
            total_steps=0,
            unique_commands=0,
            top_commands=[],
            first_step_time=None,
            last_step_time=None,
            duration_seconds=None,
            has_notes=0,
            has_tags=bool(session.tags),
        )

    freq: Dict[str, int] = {}
    for step in steps:
        cmd = step.command.strip().lower()
        freq[cmd] = freq.get(cmd, 0) + 1

    top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]

    times = []
    for step in steps:
        try:
            times.append(datetime.fromisoformat(step.timestamp))
        except Exception:
            pass

    duration = None
    first_time = None
    last_time = None
    if times:
        first_time = min(times).isoformat()
        last_time = max(times).isoformat()
        duration = (max(times) - min(times)).total_seconds()

    notes_count = sum(1 for s in steps if s.note and s.note.strip())

    return ProfileResult(
        session_id=session.id,
        session_name=session.name,
        total_steps=len(steps),
        unique_commands=len(freq),
        top_commands=top,
        first_step_time=first_time,
        last_step_time=last_time,
        duration_seconds=duration,
        has_notes=notes_count,
        has_tags=bool(session.tags),
    )


def format_profile(result: ProfileResult) -> str:
    lines = [
        f"Session : {result.session_name} ({result.session_id})",
        f"Steps   : {result.total_steps}",
        f"Unique  : {result.unique_commands} commands",
        f"Notes   : {result.has_notes} steps with notes",
        f"Tags    : {'yes' if result.has_tags else 'no'}",
    ]
    if result.first_step_time:
        lines.append(f"From    : {result.first_step_time}")
        lines.append(f"To      : {result.last_step_time}")
        lines.append(f"Span    : {result.duration_seconds:.1f}s")
    if result.top_commands:
        lines.append("Top cmds:")
        for cmd, count in result.top_commands:
            lines.append(f"  {count:>4}x  {cmd}")
    return "\n".join(lines)
