"""recycle_store.py — persist recycled sessions to disk."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from breadcrumb.recycler import RecycleEntry


class RecycleStore:
    def __init__(self, base_dir: str = "~/.breadcrumb/recycle") -> None:
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        return self.base_dir / f"{session_id}.json"

    def save(self, entry: RecycleEntry) -> None:
        self._path(entry.session.id).write_text(
            json.dumps(entry.to_dict(), indent=2), encoding="utf-8"
        )

    def load(self, session_id: str) -> RecycleEntry:
        p = self._path(session_id)
        if not p.exists():
            raise FileNotFoundError(f"No recycled session with id '{session_id}'.")
        return RecycleEntry.from_dict(json.loads(p.read_text(encoding="utf-8")))

    def delete(self, session_id: str) -> None:
        p = self._path(session_id)
        if not p.exists():
            raise FileNotFoundError(f"No recycled session with id '{session_id}'.")
        p.unlink()

    def list_entries(self) -> List[RecycleEntry]:
        entries = []
        for p in sorted(self.base_dir.glob("*.json")):
            try:
                entries.append(RecycleEntry.from_dict(json.loads(p.read_text(encoding="utf-8"))))
            except Exception:
                pass
        return entries

    def purge(self) -> int:
        """Delete all recycled sessions. Returns count removed."""
        count = 0
        for p in self.base_dir.glob("*.json"):
            p.unlink()
            count += 1
        return count
