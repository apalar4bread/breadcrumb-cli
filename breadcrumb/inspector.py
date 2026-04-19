"""Inspector: deep-dive metadata summary for a single session step."""

from dataclasses import dataclass, field
from typing import Any
from breadcrumb.session import Session, Step


class InspectError(Exception):
    pass


@dataclass
class StepInspection:
    index: int
    command: str
    note: str
    timestamp: str
    tags: list[str] = field(default_factory=list)
    label: str | None = None
    pinned: bool = False
    bookmarked: bool = False
    annotated: bool = False
    annotation: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


def inspect_step(session: Session, index: int) -> StepInspection:
    if not session.steps:
        raise InspectError("Session has no steps.")
    if index < 0 or index >= len(session.steps):
        raise InspectError(f"Step index {index} out of range (0-{len(session.steps)-1}).")

    step: Step = session.steps[index]
    meta = step.metadata or {}

    extra = {k: v for k, v in meta.items()
             if k not in {"tags", "label", "pinned", "bookmarked", "annotation"}}

    return StepInspection(
        index=index,
        command=step.command,
        note=step.note or "",
        timestamp=step.timestamp,
        tags=list(meta.get("tags", [])),
        label=meta.get("label"),
        pinned=bool(meta.get("pinned", False)),
        bookmarked=bool(meta.get("bookmarked", False)),
        annotated="annotation" in meta,
        annotation=meta.get("annotation"),
        extra=extra,
    )


def format_inspection(insp: StepInspection) -> str:
    lines = [
        f"Step #{insp.index}",
        f"  Command   : {insp.command}",
        f"  Note      : {insp.note or '(none)'}",
        f"  Timestamp : {insp.timestamp}",
        f"  Tags      : {', '.join(insp.tags) if insp.tags else '(none)'}",
        f"  Label     : {insp.label or '(none)'}",
        f"  Pinned    : {'yes' if insp.pinned else 'no'}",
        f"  Bookmarked: {'yes' if insp.bookmarked else 'no'}",
        f"  Annotation: {insp.annotation if insp.annotated else '(none)'}",
    ]
    if insp.extra:
        lines.append("  Extra metadata:")
        for k, v in insp.extra.items():
            lines.append(f"    {k}: {v}")
    return "\n".join(lines)
