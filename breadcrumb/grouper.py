"""Group session steps by a given attribute."""
from collections import defaultdict
from typing import Dict, List
from breadcrumb.session import Session, Step


class GroupError(ValueError):
    pass


VALID_KEYS = {"command", "note", "label", "tag"}


def group_by_command(session: Session) -> Dict[str, List[Step]]:
    groups: Dict[str, List[Step]] = defaultdict(list)
    for step in session.steps:
        key = step.command.strip().split()[0] if step.command.strip() else "(empty)"
        groups[key].append(step)
    return dict(groups)


def group_by_note(session: Session) -> Dict[str, List[Step]]:
    groups: Dict[str, List[Step]] = defaultdict(list)
    for step in session.steps:
        key = step.note.strip() if step.note and step.note.strip() else "(no note)"
        groups[key].append(step)
    return dict(groups)


def group_by_label(session: Session) -> Dict[str, List[Step]]:
    groups: Dict[str, List[Step]] = defaultdict(list)
    for step in session.steps:
        label = step.metadata.get("label", "").strip() or "(unlabeled)"
        groups[label].append(step)
    return dict(groups)


def group_by_tag(session: Session) -> Dict[str, List[Step]]:
    groups: Dict[str, List[Step]] = defaultdict(list)
    for step in session.steps:
        tags = step.metadata.get("tags", [])
        if not tags:
            groups["(untagged)"].append(step)
        else:
            for tag in tags:
                groups[tag].append(step)
    return dict(groups)


def group_steps(session: Session, key: str) -> Dict[str, List[Step]]:
    if key not in VALID_KEYS:
        raise GroupError(f"Invalid group key '{key}'. Choose from: {', '.join(sorted(VALID_KEYS))}")
    return {
        "command": group_by_command,
        "note": group_by_note,
        "label": group_by_label,
        "tag": group_by_tag,
    }[key](session)
