"""Detect and remove duplicate steps within or across sessions."""
from typing import List, Tuple
from breadcrumb.session import Session, Step


def _step_key(step: Step) -> str:
    return step.command.strip().lower()


def find_duplicate_steps(session: Session) -> List[Tuple[int, int]]:
    """Return list of (index_a, index_b) pairs of duplicate steps."""
    seen = {}
    duplicates = []
    for i, step in enumerate(session.steps):
        key = _step_key(step)
        if key in seen:
            duplicates.append((seen[key], i))
        else:
            seen[key] = i
    return duplicates


def remove_duplicate_steps(session: Session, keep: str = "first") -> Session:
    """Return a new session with duplicates removed.

    Args:
        session: source session
        keep: 'first' or 'last'
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    seen = {}
    for i, step in enumerate(session.steps):
        key = _step_key(step)
        if keep == "first" and key not in seen:
            seen[key] = i
        elif keep == "last":
            seen[key] = i

    kept_indices = sorted(seen.values())
    new_steps = [session.steps[i] for i in kept_indices]

    import copy
    new_session = copy.deepcopy(session)
    new_session.steps = new_steps
    return new_session


def find_common_steps(session_a: Session, session_b: Session) -> List[str]:
    """Return commands that appear in both sessions (normalized)."""
    keys_a = {_step_key(s) for s in session_a.steps}
    keys_b = {_step_key(s) for s in session_b.steps}
    return sorted(keys_a & keys_b)
