"""linker.py — Link sessions together with named relationships."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from breadcrumb.session import Session


class LinkError(Exception):
    pass


LINK_TYPES = {"depends-on", "follows", "related", "blocks"}


@dataclass
class SessionLink:
    source_id: str
    target_id: str
    link_type: str
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "link_type": self.link_type,
            "note": self.note,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionLink":
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            link_type=data["link_type"],
            note=data.get("note"),
        )


def add_link(
    session: Session,
    target_id: str,
    link_type: str,
    note: Optional[str] = None,
) -> SessionLink:
    """Attach a named link from session to target_id."""
    link_type = link_type.strip().lower()
    if link_type not in LINK_TYPES:
        raise LinkError(
            f"Invalid link type '{link_type}'. Choose from: {sorted(LINK_TYPES)}"
        )
    if not target_id or not target_id.strip():
        raise LinkError("target_id must not be empty.")
    if target_id == session.id:
        raise LinkError("A session cannot link to itself.")

    links: list = session.metadata.setdefault("links", [])
    for existing in links:
        if existing["target_id"] == target_id and existing["link_type"] == link_type:
            raise LinkError(
                f"Link '{link_type}' to '{target_id}' already exists."
            )

    link = SessionLink(
        source_id=session.id,
        target_id=target_id,
        link_type=link_type,
        note=note.strip() if note else None,
    )
    links.append(link.to_dict())
    return link


def remove_link(session: Session, target_id: str, link_type: str) -> None:
    """Remove a specific link from the session."""
    link_type = link_type.strip().lower()
    links: list = session.metadata.get("links", [])
    before = len(links)
    session.metadata["links"] = [
        lk for lk in links
        if not (lk["target_id"] == target_id and lk["link_type"] == link_type)
    ]
    if len(session.metadata["links"]) == before:
        raise LinkError(f"No '{link_type}' link to '{target_id}' found.")


def list_links(session: Session) -> list[SessionLink]:
    """Return all links attached to a session."""
    return [
        SessionLink.from_dict(lk)
        for lk in session.metadata.get("links", [])
    ]


def format_links(links: list[SessionLink]) -> str:
    if not links:
        return "No links."
    lines = []
    for lk in links:
        note_part = f" — {lk.note}" if lk.note else ""
        lines.append(f"  [{lk.link_type}] → {lk.target_id}{note_part}")
    return "\n".join(lines)
