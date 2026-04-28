"""capper.py — enforce a maximum number of steps in a session, dropping oldest or newest."""

from dataclasses import dataclass
from typing import Literal

from breadcrumb.session import Session


class CapError(Exception):
    pass


@dataclass
class CapResult:
    session: Session
    original_count: int
    removed_count: int
    strategy: str

    @property
    def kept_count(self) -> int:
        return len(self.session.steps)

    def summary(self) -> str:
        if self.removed_count == 0:
            return f"Session already within cap ({self.kept_count} steps)."
        return (
            f"Capped '{self.session.name}': kept {self.kept_count} of "
            f"{self.original_count} steps (removed {self.removed_count} "
            f"from {'start' if self.strategy == 'oldest' else 'end'})."
        )


def cap_session(
    session: Session,
    max_steps: int,
    strategy: Literal["oldest", "newest"] = "oldest",
) -> CapResult:
    """Trim a session so it has at most *max_steps* steps.

    strategy='oldest'  → drop steps from the beginning (keep newest)
    strategy='newest'  → drop steps from the end (keep oldest)
    """
    if max_steps < 1:
        raise CapError(f"max_steps must be >= 1, got {max_steps}")
    if strategy not in ("oldest", "newest"):
        raise CapError(f"Unknown strategy '{strategy}'; use 'oldest' or 'newest'.")

    original_count = len(session.steps)
    if original_count <= max_steps:
        return CapResult(
            session=session,
            original_count=original_count,
            removed_count=0,
            strategy=strategy,
        )

    if strategy == "oldest":
        session.steps = session.steps[original_count - max_steps :]
    else:
        session.steps = session.steps[:max_steps]

    removed = original_count - len(session.steps)
    return CapResult(
        session=session,
        original_count=original_count,
        removed_count=removed,
        strategy=strategy,
    )
