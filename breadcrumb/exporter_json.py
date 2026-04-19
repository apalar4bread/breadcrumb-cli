"""Export a session to a pretty-printed JSON file."""

from __future__ import annotations

import json
from pathlib import Path

from breadcrumb.session import Session


class JsonExportError(Exception):
    pass


def export_to_json(session: Session, indent: int = 2) -> str:
    """Return a JSON string representation of the session."""
    data = {
        "id": session.id,
        "name": session.name,
        "created_at": session.created_at,
        "tags": list(session.tags),
        "metadata": session.metadata,
        "steps": [
            {
                "index": i + 1,
                "command": step.command,
                "note": step.note,
                "timestamp": step.timestamp,
                "metadata": step.metadata,
            }
            for i, step in enumerate(session.steps)
        ],
    }
    return json.dumps(data, indent=indent, default=str)


def write_json(session: Session, path: str | Path, indent: int = 2) -> Path:
    """Write the session as JSON to *path*.

    The file must have a .json extension.
    Raises JsonExportError otherwise.
    """
    dest = Path(path)
    if dest.suffix.lower() != ".json":
        raise JsonExportError(f"Output file must have a .json extension, got: {dest.suffix!r}")
    dest.write_text(export_to_json(session, indent=indent), encoding="utf-8")
    return dest
