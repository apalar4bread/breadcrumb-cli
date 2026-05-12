"""flagger.py — mark steps with custom flags for quick categorisation."""
from __future__ import annotations

from breadcrumb.session import Session


class FlagError(Exception):
    pass


_META_KEY = "flags"
_VALID_FLAGS = {"todo", "done", "skip", "review", "warn"}


def _get_flags(step) -> list[str]:
    return list(step.metadata.get(_META_KEY, []))


def set_flag(session: Session, index: int, flag: str) -> None:
    """Add *flag* to the step at *index* (idempotent)."""
    flag = flag.strip().lower()
    if not flag:
        raise FlagError("Flag name must not be empty.")
    if flag not in _VALID_FLAGS:
        raise FlagError(f"Unknown flag '{flag}'. Valid flags: {sorted(_VALID_FLAGS)}")
    if index < 0 or index >= len(session.steps):
        raise FlagError(f"Step index {index} out of range.")
    step = session.steps[index]
    flags = _get_flags(step)
    if flag not in flags:
        flags.append(flag)
        step.metadata[_META_KEY] = flags


def clear_flag(session: Session, index: int, flag: str) -> None:
    """Remove *flag* from the step at *index* (no-op if absent)."""
    flag = flag.strip().lower()
    if index < 0 or index >= len(session.steps):
        raise FlagError(f"Step index {index} out of range.")
    step = session.steps[index]
    flags = _get_flags(step)
    step.metadata[_META_KEY] = [f for f in flags if f != flag]


def get_flags(session: Session, index: int) -> list[str]:
    """Return the list of flags on the step at *index*."""
    if index < 0 or index >= len(session.steps):
        raise FlagError(f"Step index {index} out of range.")
    return _get_flags(session.steps[index])


def find_by_flag(session: Session, flag: str) -> list[int]:
    """Return indices of all steps that carry *flag*."""
    flag = flag.strip().lower()
    return [i for i, s in enumerate(session.steps) if flag in _get_flags(s)]


def clear_all_flags(session: Session, index: int) -> None:
    """Remove every flag from the step at *index*."""
    if index < 0 or index >= len(session.steps):
        raise FlagError(f"Step index {index} out of range.")
    session.steps[index].metadata.pop(_META_KEY, None)
