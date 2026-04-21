"""Digest a session into a compact summary hash and change fingerprint."""

import hashlib
import json
from dataclasses import dataclass
from typing import List

from breadcrumb.session import Session


class DigestError(Exception):
    pass


@dataclass
class DigestResult:
    session_id: str
    session_name: str
    step_count: int
    fingerprint: str  # SHA-256 of all commands in order
    command_hash: str  # SHA-256 of sorted unique commands
    is_empty: bool

    def short(self) -> str:
        """Return first 12 chars of fingerprint."""
        return self.fingerprint[:12]


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def digest_session(session: Session) -> DigestResult:
    """Compute a digest/fingerprint for a session based on its steps."""
    if not session.steps:
        return DigestResult(
            session_id=session.id,
            session_name=session.name,
            step_count=0,
            fingerprint=_sha256(""),
            command_hash=_sha256(""),
            is_empty=True,
        )

    commands_in_order = [s.command for s in session.steps]
    fingerprint_input = json.dumps(commands_in_order, separators=(",", ":"))
    fingerprint = _sha256(fingerprint_input)

    sorted_unique = sorted(set(c.lower() for c in commands_in_order))
    command_hash = _sha256(json.dumps(sorted_unique, separators=(",", ":")))

    return DigestResult(
        session_id=session.id,
        session_name=session.name,
        step_count=len(session.steps),
        fingerprint=fingerprint,
        command_hash=command_hash,
        is_empty=False,
    )


def digests_match(a: DigestResult, b: DigestResult) -> bool:
    """Return True if two digests have the same ordered fingerprint."""
    return a.fingerprint == b.fingerprint


def format_digest(result: DigestResult) -> str:
    """Format a DigestResult for display."""
    lines = [
        f"Session : {result.session_name} ({result.session_id})",
        f"Steps   : {result.step_count}",
        f"Fingerprint : {result.fingerprint}",
        f"Cmd hash    : {result.command_hash}",
        f"Empty   : {result.is_empty}",
    ]
    return "\n".join(lines)
