"""Tag management for breadcrumb sessions."""
from typing import List
from breadcrumb.session import Session
from breadcrumb.store import SessionStore


def add_tag(session: Session, tag: str) -> Session:
    """Add a tag to a session if not already present."""
    tag = tag.strip().lower()
    if not tag:
        raise ValueError("Tag cannot be empty")
    if tag not in session.tags:
        session.tags.append(tag)
    return session


def remove_tag(session: Session, tag: str) -> Session:
    """Remove a tag from a session."""
    tag = tag.strip().lower()
    if tag in session.tags:
        session.tags.remove(tag)
    return session


def list_tags(session: Session) -> List[str]:
    """Return sorted list of tags for a session."""
    return sorted(session.tags)


def find_by_tag(store: SessionStore, tag: str) -> List[Session]:
    """Find all sessions that have a given tag."""
    tag = tag.strip().lower()
    results = []
    for name in store.list_sessions():
        session = store.load(name)
        if session and tag in session.tags:
            results.append(session)
    return results
