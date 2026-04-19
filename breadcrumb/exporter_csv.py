"""Export sessions to CSV format."""
import csv
import io
from pathlib import Path
from breadcrumb.session import Session


CSV_FIELDS = ["step", "command", "note", "timestamp", "tags", "label", "pinned", "bookmarked"]


def export_to_csv(session: Session) -> str:
    """Return CSV string for the session's steps."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for i, step in enumerate(session.steps, start=1):
        meta = step.metadata or {}
        writer.writerow({
            "step": i,
            "command": step.command,
            "note": step.note or "",
            "timestamp": step.timestamp,
            "tags": "|".join(meta.get("tags", [])),
            "label": meta.get("label", ""),
            "pinned": "yes" if meta.get("pinned") else "no",
            "bookmarked": "yes" if meta.get("bookmarked") else "no",
        })
    return output.getvalue()


def write_csv(session: Session, path: str) -> Path:
    """Write CSV export to a file and return the path."""
    out = Path(path)
    if out.suffix.lower() != ".csv":
        raise ValueError(f"Output file must have .csv extension, got: {path}")
    out.write_text(export_to_csv(session), encoding="utf-8")
    return out
