"""Assign priority/status labels to steps."""

VALID_LABELS = {"low", "medium", "high", "critical", "done", "todo", "skip"}
_META_KEY = "label"


class LabelError(Exception):
    pass


def set_label(session, step_index: int, label: str) -> None:
    """Assign a label to a step."""
    label = label.strip().lower()
    if not label:
        raise LabelError("Label must not be empty.")
    if label not in VALID_LABELS:
        raise LabelError(f"Invalid label '{label}'. Choose from: {sorted(VALID_LABELS)}")
    if step_index < 0 or step_index >= len(session.steps):
        raise LabelError(f"Step index {step_index} out of range.")
    session.steps[step_index].metadata[_META_KEY] = label


def clear_label(session, step_index: int) -> None:
    """Remove label from a step if present."""
    if step_index < 0 or step_index >= len(session.steps):
        raise LabelError(f"Step index {step_index} out of range.")
    session.steps[step_index].metadata.pop(_META_KEY, None)


def get_label(session, step_index: int) -> str | None:
    """Return the label for a step, or None."""
    if step_index < 0 or step_index >= len(session.steps):
        raise LabelError(f"Step index {step_index} out of range.")
    return session.steps[step_index].metadata.get(_META_KEY)


def find_by_label(session, label: str) -> list[tuple[int, object]]:
    """Return list of (index, step) tuples matching the given label."""
    label = label.strip().lower()
    return [
        (i, s) for i, s in enumerate(session.steps)
        if s.metadata.get(_META_KEY) == label
    ]


def label_summary(session) -> dict[str, int]:
    """Return a count of steps per label across the session.

    Unlabelled steps are not included in the result.
    """
    summary: dict[str, int] = {}
    for step in session.steps:
        label = step.metadata.get(_META_KEY)
        if label is not None:
            summary[label] = summary.get(label, 0) + 1
    return summary
