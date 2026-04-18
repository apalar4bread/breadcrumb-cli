"""Schedule steps to run at specific intervals or times."""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


class ScheduleError(Exception):
    pass


VALID_INTERVALS = {"minutely", "hourly", "daily", "weekly"}


@dataclass
class Schedule:
    session_id: str
    interval: str
    next_run: Optional[str] = None
    enabled: bool = True
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "interval": self.interval,
            "next_run": self.next_run,
            "enabled": self.enabled,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Schedule":
        return cls(
            session_id=d["session_id"],
            interval=d["interval"],
            next_run=d.get("next_run"),
            enabled=d.get("enabled", True),
            notes=d.get("notes", ""),
        )


def set_schedule(session_id: str, interval: str, notes: str = "") -> Schedule:
    interval = interval.lower().strip()
    if interval not in VALID_INTERVALS:
        raise ScheduleError(f"Invalid interval '{interval}'. Choose from: {', '.join(sorted(VALID_INTERVALS))}")
    if not session_id or not session_id.strip():
        raise ScheduleError("session_id cannot be empty")
    return Schedule(session_id=session_id.strip(), interval=interval, notes=notes)


def disable_schedule(schedule: Schedule) -> Schedule:
    schedule.enabled = False
    return schedule


def enable_schedule(schedule: Schedule) -> Schedule:
    schedule.enabled = True
    return schedule


def describe_schedule(schedule: Schedule) -> str:
    status = "enabled" if schedule.enabled else "disabled"
    parts = [f"Session: {schedule.session_id}", f"Interval: {schedule.interval}", f"Status: {status}"]
    if schedule.next_run:
        parts.append(f"Next run: {schedule.next_run}")
    if schedule.notes:
        parts.append(f"Notes: {schedule.notes}")
    return "\n".join(parts)
