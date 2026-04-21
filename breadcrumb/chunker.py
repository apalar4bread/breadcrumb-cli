"""Split a session's steps into fixed-size chunks."""

from dataclasses import dataclass, field
from typing import List

from breadcrumb.session import Session, Step


class ChunkError(Exception):
    pass


@dataclass
class Chunk:
    index: int
    steps: List[Step] = field(default_factory=list)

    @property
    def size(self) -> int:
        return len(self.steps)


def chunk_session(session: Session, size: int) -> List[Chunk]:
    """Divide session steps into chunks of *size* steps each."""
    if size < 1:
        raise ChunkError(f"Chunk size must be >= 1, got {size}")
    if not session.steps:
        raise ChunkError("Cannot chunk a session with no steps")

    chunks: List[Chunk] = []
    for i, start in enumerate(range(0, len(session.steps), size)):
        chunk = Chunk(index=i, steps=list(session.steps[start : start + size]))
        chunks.append(chunk)
    return chunks


def chunk_to_sessions(session: Session, size: int) -> List[Session]:
    """Return a list of new Session objects, one per chunk."""
    chunks = chunk_session(session, size)
    result: List[Session] = []
    for chunk in chunks:
        new_session = Session(
            name=f"{session.name} (chunk {chunk.index + 1}/{len(chunks)})",
            tags=list(session.tags),
        )
        new_session.steps = [Step(**{**s.__dict__}) for s in chunk.steps]
        result.append(new_session)
    return result


def format_chunk_summary(chunks: List[Chunk]) -> str:
    """Human-readable summary of chunk breakdown."""
    lines = [f"Total chunks: {len(chunks)}"]
    for c in chunks:
        lines.append(f"  Chunk {c.index + 1}: {c.size} step(s)")
    return "\n".join(lines)
