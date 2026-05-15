"""Plan future steps for a session without executing them."""

from dataclasses import dataclass, field
from typing import List, Optional
from breadcrumb.session import Session, Step
import datetime


class PlanError(Exception):
    pass


@dataclass
class PlannedStep:
    command: str
    note: str = ""
    order: int = 0
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "note": self.note,
            "order": self.order,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlannedStep":
        return cls(
            command=data["command"],
            note=data.get("note", ""),
            order=data.get("order", 0),
            metadata=data.get("metadata", {}),
        )


@dataclass
class PlanResult:
    session_id: str
    planned: List[PlannedStep] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.planned)

    def summary(self) -> str:
        return f"{self.count} step(s) planned for session {self.session_id}"


def add_planned_step(
    session: Session,
    command: str,
    note: str = "",
    order: Optional[int] = None,
) -> PlannedStep:
    if not command or not command.strip():
        raise PlanError("Planned step command must not be empty.")
    command = command.strip()
    planned = session.metadata.setdefault("planned_steps", [])
    if order is None:
        order = len(planned)
    step = PlannedStep(command=command, note=note.strip(), order=order)
    planned.append(step.to_dict())
    return step


def list_planned(session: Session) -> List[PlannedStep]:
    raw = session.metadata.get("planned_steps", [])
    return sorted(
        [PlannedStep.from_dict(s) for s in raw], key=lambda s: s.order
    )


def clear_planned(session: Session) -> int:
    existing = session.metadata.pop("planned_steps", [])
    return len(existing)


def promote_planned(session: Session, order: int) -> Step:
    """Promote a planned step to a real session step and remove it from the plan."""
    planned = session.metadata.get("planned_steps", [])
    match = next((s for s in planned if s["order"] == order), None)
    if match is None:
        raise PlanError(f"No planned step with order {order}.")
    planned.remove(match)
    from breadcrumb.session import add_step
    step = add_step(session, command=match["command"], note=match.get("note", ""))
    return step
