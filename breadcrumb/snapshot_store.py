"""Persist snapshots to disk alongside sessions."""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Optional
from breadcrumb.snapshotter import Snapshot


class SnapshotStore:
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str, label: str) -> Path:
        safe = label.replace("/", "_").replace(" ", "_")
        return self.base_dir / f"{session_id}__{safe}.snapshot.json"

    def save(self, snapshot: Snapshot, label: str) -> Path:
        p = self._path(snapshot.session_id, label)
        p.write_text(json.dumps(snapshot.to_dict(), indent=2))
        return p

    def load(self, session_id: str, label: str) -> Snapshot:
        p = self._path(session_id, label)
        if not p.exists():
            raise FileNotFoundError(f"No snapshot '{label}' for session {session_id}.")
        return Snapshot.from_dict(json.loads(p.read_text()))

    def list_snapshots(self, session_id: str) -> List[str]:
        prefix = f"{session_id}__"
        labels = []
        for f in sorted(self.base_dir.glob(f"{prefix}*.snapshot.json")):
            stem = f.stem.replace(".snapshot", "")
            label = stem[len(prefix):]
            labels.append(label)
        return labels

    def delete(self, session_id: str, label: str) -> bool:
        p = self._path(session_id, label)
        if p.exists():
            p.unlink()
            return True
        return False

    def rename(self, session_id: str, old_label: str, new_label: str) -> Path:
        """Rename a snapshot label. Returns the new path."""
        old_path = self._path(session_id, old_label)
        if not old_path.exists():
            raise FileNotFoundError(f"No snapshot '{old_label}' for session {session_id}.")
        new_path = self._path(session_id, new_label)
        if new_path.exists():
            raise FileExistsError(f"A snapshot named '{new_label}' already exists for session {session_id}.")
        old_path.rename(new_path)
        return new_path
