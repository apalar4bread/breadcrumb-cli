"""Annotate steps with inline comments for export and display."""

from breadcrumb.session import Session, Step


class AnnotateError(Exception):
    pass


def annotate_step(session: Session, index: int, comment: str) -> Step:
    """Set or replace the comment annotation on a step."""
    if not comment or not comment.strip():
        raise AnnotateError("Comment must not be empty.")
    if index < 0 or index >= len(session.steps):
        raise AnnotateError(f"Step index {index} out of range.")
    step = session.steps[index]
    step.metadata["comment"] = comment.strip()
    return step


def clear_annotation(session: Session, index: int) -> Step:
    """Remove the comment annotation from a step."""
    if index < 0 or index >= len(session.steps):
        raise AnnotateError(f"Step index {index} out of range.")
    step = session.steps[index]
    step.metadata.pop("comment", None)
    return step


def get_annotation(step: Step) -> str | None:
    """Return the comment annotation for a step, or None."""
    return step.metadata.get("comment")


def list_annotated(session: Session) -> list[tuple[int, Step]]:
    """Return list of (index, step) tuples where a comment exists."""
    return [
        (i, s) for i, s in enumerate(session.steps)
        if "comment" in s.metadata
    ]
