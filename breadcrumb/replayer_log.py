"""Replay logger — records the outcome of each replayed step into a structured log."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from breadcrumb.session import Session


@dataclass
class ReplayLogEntry:
    step_index: int
    command: str
    exit_code: int
    stdout: str
    stderr: str
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    skipped: bool = False

    def to_dict(self) -> dict:
        return {
            "step_index": self.step_index,
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "executed_at": self.executed_at,
            "skipped": self.skipped,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReplayLogEntry":
        return cls(
            step_index=data["step_index"],
            command=data["command"],
            exit_code=data["exit_code"],
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            executed_at=data.get("executed_at", ""),
            skipped=data.get("skipped", False),
        )


@dataclass
class ReplayLog:
    session_id: str
    session_name: str
    entries: List[ReplayLogEntry] = field(default_factory=list)
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: Optional[str] = None

    def record(self, entry: ReplayLogEntry) -> None:
        self.entries.append(entry)

    def finish(self) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat()

    @property
    def success_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped and e.exit_code == 0)

    @property
    def failure_count(self) -> int:
        return sum(1 for e in self.entries if not e.skipped and e.exit_code != 0)

    @property
    def skipped_count(self) -> int:
        return sum(1 for e in self.entries if e.skipped)

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "entries": [e.to_dict() for e in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReplayLog":
        log = cls(
            session_id=data["session_id"],
            session_name=data["session_name"],
            started_at=data.get("started_at", ""),
        )
        log.finished_at = data.get("finished_at")
        log.entries = [ReplayLogEntry.from_dict(e) for e in data.get("entries", [])]
        return log


def create_log(session: Session) -> ReplayLog:
    return ReplayLog(session_id=session.id, session_name=session.name)


def format_log(log: ReplayLog) -> str:
    lines = [
        f"Replay log for '{log.session_name}' ({log.session_id})",
        f"  Started : {log.started_at}",
        f"  Finished: {log.finished_at or 'in progress'}",
        f"  Steps   : {len(log.entries)} total, {log.success_count} ok, "
        f"{log.failure_count} failed, {log.skipped_count} skipped",
        "",
    ]
    for e in log.entries:
        status = "SKIP" if e.skipped else ("OK" if e.exit_code == 0 else f"FAIL({e.exit_code})")
        lines.append(f"  [{e.step_index + 1:>3}] {status:<10} {e.command}")
        if e.stderr:
            lines.append(f"             stderr: {e.stderr.strip()[:80]}")
    return "\n".join(lines)
