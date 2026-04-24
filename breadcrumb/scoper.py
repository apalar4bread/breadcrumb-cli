"""Scoper: assign and query scope levels on session steps.

Scopes allow steps to be tagged with a logical execution context,
e.g. 'local', 'staging', 'production', or any custom string.
"""

from __future__ import annotations

from typing import List, Optional

from breadcrumb.session import Session, Step

VALID_SCOPES = {"local", "staging", "production", "test", "ci"}
SCOPE_KEY = "scope"


class ScopeError(Exception):
    pass


def set_scope(session: Session, step_index: int, scope: str) -> Step:
    """Assign a scope to a step. Normalizes to lowercase."""
    scope = scope.strip().lower()
    if not scope:
        raise ScopeError("Scope must not be empty.")
    if scope not in VALID_SCOPES:
        raise ScopeError(
            f"Invalid scope '{scope}'. Valid scopes: {sorted(VALID_SCOPES)}"
        )
    if step_index < 0 or step_index >= len(session.steps):
        raise ScopeError(f"Step index {step_index} out of range.")
    step = session.steps[step_index]
    step.metadata[SCOPE_KEY] = scope
    return step


def clear_scope(session: Session, step_index: int) -> Step:
    """Remove the scope from a step if present."""
    if step_index < 0 or step_index >= len(session.steps):
        raise ScopeError(f"Step index {step_index} out of range.")
    step = session.steps[step_index]
    step.metadata.pop(SCOPE_KEY, None)
    return step


def get_scope(session: Session, step_index: int) -> Optional[str]:
    """Return the scope of a step, or None if not set."""
    if step_index < 0 or step_index >= len(session.steps):
        raise ScopeError(f"Step index {step_index} out of range.")
    return session.steps[step_index].metadata.get(SCOPE_KEY)


def filter_by_scope(session: Session, scope: str) -> List[Step]:
    """Return all steps that match the given scope (case-insensitive)."""
    scope = scope.strip().lower()
    return [
        step
        for step in session.steps
        if step.metadata.get(SCOPE_KEY, "").lower() == scope
    ]


def list_scoped(session: Session) -> List[tuple[int, Step, str]]:
    """Return list of (index, step, scope) for all steps that have a scope."""
    result = []
    for i, step in enumerate(session.steps):
        scope = step.metadata.get(SCOPE_KEY)
        if scope:
            result.append((i, step, scope))
    return result
