"""Paginator — slice a session's steps into pages for display or processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import ceil
from typing import List

from breadcrumb.session import Session, Step


class PaginatorError(Exception):
    """Raised when pagination parameters are invalid."""


@dataclass
class Page:
    """A single page of steps."""

    number: int          # 1-based page number
    total_pages: int
    steps: List[Step] = field(default_factory=list)

    @property
    def is_first(self) -> bool:
        return self.number == 1

    @property
    def is_last(self) -> bool:
        return self.number == self.total_pages

    @property
    def size(self) -> int:
        return len(self.steps)


@dataclass
class PaginateResult:
    """Result of paginating a session."""

    session_name: str
    page_size: int
    total_steps: int
    pages: List[Page] = field(default_factory=list)

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    def get_page(self, number: int) -> Page:
        """Return a page by 1-based page number."""
        if number < 1 or number > self.total_pages:
            raise PaginatorError(
                f"Page {number} out of range (1–{self.total_pages})."
            )
        return self.pages[number - 1]


def paginate_session(session: Session, page_size: int = 10) -> PaginateResult:
    """Split *session* steps into pages of *page_size*.

    Args:
        session:   The session whose steps will be paginated.
        page_size: Number of steps per page (must be >= 1).

    Returns:
        A :class:`PaginateResult` containing all pages.

    Raises:
        PaginatorError: If *page_size* is less than 1.
    """
    if page_size < 1:
        raise PaginatorError(f"page_size must be >= 1, got {page_size}.")

    steps = session.steps
    total = len(steps)
    total_pages = ceil(total / page_size) if total else 1

    pages: List[Page] = []
    for i in range(total_pages):
        start = i * page_size
        end = start + page_size
        pages.append(
            Page(
                number=i + 1,
                total_pages=total_pages,
                steps=steps[start:end],
            )
        )

    # Guarantee at least one (empty) page even for empty sessions.
    if not pages:
        pages.append(Page(number=1, total_pages=1, steps=[]))

    return PaginateResult(
        session_name=session.name,
        page_size=page_size,
        total_steps=total,
        pages=pages,
    )


def format_page(page: Page, *, show_index: bool = True) -> str:
    """Return a human-readable string for a single page.

    Args:
        page:        The page to format.
        show_index:  Prefix each step with its 1-based position on the page.
    """
    lines: List[str] = [
        f"--- Page {page.number}/{page.total_pages} ({page.size} step(s)) ---"
    ]
    for i, step in enumerate(page.steps, start=1):
        prefix = f"{i:>3}. " if show_index else "     "
        note_part = f"  # {step.note}" if step.note else ""
        lines.append(f"{prefix}{step.command}{note_part}")
    if not page.steps:
        lines.append("     (no steps)")
    return "\n".join(lines)
