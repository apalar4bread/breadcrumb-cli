"""pipeline.py — chain multiple session transformations into a single pass.

A Pipeline is an ordered list of named operations applied sequentially
to a Session.  Each operation is a callable that accepts a Session and
returns a (possibly new) Session.  Results from each stage are fed into
the next, making it easy to compose trimming, filtering, sorting, and
other transforms without intermediate saves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from breadcrumb.session import Session

# Type alias for a single pipeline stage.
StageFunc = Callable[[Session], Session]


class PipelineError(Exception):
    """Raised when a pipeline stage fails."""


@dataclass
class Stage:
    """A named transformation stage."""

    name: str
    func: StageFunc

    def apply(self, session: Session) -> Session:
        """Run this stage, wrapping exceptions in PipelineError."""
        try:
            return self.func(session)
        except PipelineError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise PipelineError(
                f"Stage '{self.name}' failed: {exc}"
            ) from exc


@dataclass
class Pipeline:
    """An ordered sequence of stages applied to a Session."""

    name: str
    stages: List[Stage] = field(default_factory=list)

    def add_stage(self, name: str, func: StageFunc) -> "Pipeline":
        """Append a stage and return *self* for chaining."""
        if not name or not name.strip():
            raise PipelineError("Stage name must not be blank.")
        self.stages.append(Stage(name=name.strip(), func=func))
        return self

    def remove_stage(self, name: str) -> bool:
        """Remove the first stage with *name*.  Return True if removed."""
        for i, stage in enumerate(self.stages):
            if stage.name == name:
                del self.stages[i]
                return True
        return False

    def run(self, session: Session) -> Session:
        """Execute all stages in order and return the final Session."""
        if not self.stages:
            raise PipelineError("Pipeline has no stages to run.")
        result = session
        for stage in self.stages:
            result = stage.apply(result)
        return result

    def stage_names(self) -> List[str]:
        """Return the ordered list of stage names."""
        return [s.name for s in self.stages]


# ---------------------------------------------------------------------------
# Convenience builders
# ---------------------------------------------------------------------------


def create_pipeline(name: str) -> Pipeline:
    """Create an empty Pipeline with the given name."""
    if not name or not name.strip():
        raise PipelineError("Pipeline name must not be blank.")
    return Pipeline(name=name.strip())


def run_pipeline(
    pipeline: Pipeline,
    session: Session,
    *,
    stop_on_error: bool = True,
) -> tuple[Session, list[str]]:
    """Run *pipeline* on *session*, collecting stage names that succeeded.

    Parameters
    ----------
    pipeline:
        The pipeline to execute.
    session:
        The starting session.
    stop_on_error:
        If True (default) re-raise the first PipelineError encountered.
        If False, skip failing stages and record their names in the
        returned error list.

    Returns
    -------
    (final_session, errors)
        *final_session* is the session after all successful stages.
        *errors* is a list of ``"stage_name: message"`` strings for any
        stages that were skipped (only non-empty when stop_on_error=False).
    """
    if not pipeline.stages:
        raise PipelineError("Pipeline has no stages to run.")

    result = session
    errors: list[str] = []

    for stage in pipeline.stages:
        try:
            result = stage.apply(result)
        except PipelineError as exc:
            if stop_on_error:
                raise
            errors.append(f"{stage.name}: {exc}")

    return result, errors


def format_pipeline(pipeline: Pipeline, *, show_count: bool = True) -> str:
    """Return a human-readable summary of the pipeline."""
    lines = [f"Pipeline: {pipeline.name}"]
    if not pipeline.stages:
        lines.append("  (no stages)")
    else:
        for i, stage in enumerate(pipeline.stages, 1):
            prefix = f"  {i}." if show_count else "  -"
            lines.append(f"{prefix} {stage.name}")
    return "\n".join(lines)
