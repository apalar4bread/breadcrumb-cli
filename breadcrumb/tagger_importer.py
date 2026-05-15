"""Import tags from external sources into sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from breadcrumb.session import Session
from breadcrumb.tagger import add_tag


class TagImportError(Exception):
    pass


@dataclass
class TagImportResult:
    session_name: str
    tags_added: List[str] = field(default_factory=list)
    tags_skipped: List[str] = field(default_factory=list)

    @property
    def added_count(self) -> int:
        return len(self.tags_added)

    @property
    def skipped_count(self) -> int:
        return len(self.tags_skipped)

    def summary(self) -> str:
        return (
            f"Session '{self.session_name}': "
            f"{self.added_count} tag(s) added, "
            f"{self.skipped_count} skipped."
        )


def import_tags_from_dict(session: Session, data: Dict[str, List[str]]) -> TagImportResult:
    """Import tags from a dict mapping session names to tag lists."""
    if not session.id:
        raise TagImportError("Session must have an ID.")

    result = TagImportResult(session_name=session.name)
    raw_tags = data.get(session.name, [])

    for tag in raw_tags:
        tag = tag.strip().lower()
        if not tag:
            result.tags_skipped.append(tag)
            continue
        if tag in session.tags:
            result.tags_skipped.append(tag)
            continue
        add_tag(session, tag)
        result.tags_added.append(tag)

    return result


def import_tags_from_list(session: Session, tags: List[str]) -> TagImportResult:
    """Import a flat list of tags into a session."""
    return import_tags_from_dict(session, {session.name: tags})


def import_tags_from_text(session: Session, text: str) -> TagImportResult:
    """Import comma- or newline-separated tags from a plain text string."""
    raw = text.replace("\n", ",")
    tags = [t.strip() for t in raw.split(",")]
    return import_tags_from_list(session, tags)
