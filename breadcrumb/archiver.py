"""Archive and restore sessions to/from a portable JSON archive file."""

import json
from pathlib import Path
from datetime import datetime
from typing import List

from breadcrumb.session import Session, to_dict, from_dict


class ArchiveError(Exception):
    pass


def export_archive(sessions: List[Session], path: str) -> Path:
    """Write a list of sessions to a JSON archive file."""
    out = Path(path)
    if out.suffix != ".json":
        raise ArchiveError(f"Archive path must end in .json, got: {path}")
    payload = {
        "breadcrumb_archive": True,
        "created_at": datetime.utcnow().isoformat(),
        "sessions": [to_dict(s) for s in sessions],
    }
    out.write_text(json.dumps(payload, indent=2))
    return out


def import_archive(path: str) -> List[Session]:
    """Read sessions from a JSON archive file."""
    src = Path(path)
    if not src.exists():
        raise ArchiveError(f"Archive file not found: {path}")
    try:
        payload = json.loads(src.read_text())
    except json.JSONDecodeError as e:
        raise ArchiveError(f"Invalid JSON in archive: {e}")
    if not payload.get("breadcrumb_archive"):
        raise ArchiveError("File does not appear to be a breadcrumb archive.")
    return [from_dict(d) for d in payload.get("sessions", [])]


def archive_summary(path: str) -> dict:
    """Return metadata about an archive without fully importing it."""
    sessions = import_archive(path)
    return {
        "path": path,
        "session_count": len(sessions),
        "session_names": [s.name for s in sessions],
        "total_steps": sum(len(s.steps) for s in sessions),
    }
