"""Persistence layer — saves/loads sessions as JSON files."""

import os
import json
from pathlib import Path
from typing import List, Optional
from breadcrumb.session import Session

DEFAULT_STORE_DIR = Path.home() / ".breadcrumb" / "sessions"


class SessionStore:
    def __init__(self, store_dir: Path = DEFAULT_STORE_DIR):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

    def _session_path(self, name: str) -> Path:
        return self.store_dir / f"{name}.json"

    def save(self, session: Session) -> None:
        path = self._session_path(session.name)
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load(self, name: str) -> Session:
        path = self._session_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Session '{name}' not found.")
        with open(path) as f:
            data = json.load(f)
        return Session.from_dict(data)

    def list_sessions(self) -> List[str]:
        return [p.stem for p in sorted(self.store_dir.glob("*.json"))]

    def delete(self, name: str) -> None:
        path = self._session_path(name)
        if not path.exists():
            raise FileNotFoundError(f"Session '{name}' not found.")
        path.unlink()

    def exists(self, name: str) -> bool:
        return self._session_path(name).exists()
