"""Persist schedules to disk."""
import json
from pathlib import Path
from typing import List, Optional
from breadcrumb.scheduler import Schedule, ScheduleError


class ScheduleStore:
    def __init__(self, base_dir: str = "~/.breadcrumb/schedules"):
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.base_dir / f"{session_id}.json"

    def save(self, schedule: Schedule) -> None:
        self._path(schedule.session_id).write_text(json.dumps(schedule.to_dict(), indent=2))

    def load(self, session_id: str) -> Schedule:
        p = self._path(session_id)
        if not p.exists():
            raise ScheduleError(f"No schedule found for session '{session_id}'")
        return Schedule.from_dict(json.loads(p.read_text()))

    def delete(self, session_id: str) -> None:
        p = self._path(session_id)
        if not p.exists():
            raise ScheduleError(f"No schedule found for session '{session_id}'")
        p.unlink()

    def list_schedules(self) -> List[Schedule]:
        return [Schedule.from_dict(json.loads(f.read_text())) for f in sorted(self.base_dir.glob("*.json"))]
