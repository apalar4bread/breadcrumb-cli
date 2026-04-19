"""Watch a session and alert when step count or command patterns exceed thresholds."""

from dataclasses import dataclass, field
from typing import List, Optional
from breadcrumb.session import Session


class WatchdogError(Exception):
    pass


@dataclass
class WatchdogAlert:
    kind: str  # 'step_limit', 'command_pattern'
    message: str
    step_index: Optional[int] = None


@dataclass
class WatchdogRule:
    max_steps: Optional[int] = None
    forbidden_patterns: List[str] = field(default_factory=list)
    case_sensitive: bool = False


def check_session(session: Session, rule: WatchdogRule) -> List[WatchdogAlert]:
    alerts: List[WatchdogAlert] = []

    if rule.max_steps is not None and len(session.steps) > rule.max_steps:
        alerts.append(WatchdogAlert(
            kind="step_limit",
            message=f"Session '{session.name}' has {len(session.steps)} steps, limit is {rule.max_steps}."
        ))

    for i, step in enumerate(session.steps):
        cmd = step.command if rule.case_sensitive else step.command.lower()
        for pattern in rule.forbidden_patterns:
            p = pattern if rule.case_sensitive else pattern.lower()
            if p in cmd:
                alerts.append(WatchdogAlert(
                    kind="command_pattern",
                    message=f"Step {i} matches forbidden pattern '{pattern}': {step.command}",
                    step_index=i
                ))

    return alerts


def format_alerts(alerts: List[WatchdogAlert]) -> str:
    if not alerts:
        return "No alerts."
    lines = []
    for a in alerts:
        prefix = f"[{a.kind}]"
        lines.append(f"{prefix} {a.message}")
    return "\n".join(lines)
