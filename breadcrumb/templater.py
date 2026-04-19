"""Create and apply session templates."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from breadcrumb.session import Session, add_step


class TemplateError(Exception):
    pass


@dataclass
class Template:
    name: str
    description: str = ""
    commands: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "commands": self.commands,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Template":
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            commands=data.get("commands", []),
            tags=data.get("tags", []),
        )


def create_template(name: str, commands: List[str], description: str = "", tags: Optional[List[str]] = None) -> Template:
    name = name.strip()
    if not name:
        raise TemplateError("Template name cannot be blank.")
    if not commands:
        raise TemplateError("Template must have at least one command.")
    return Template(name=name, description=description, commands=commands, tags=tags or [])


def apply_template(template: Template, session: Session) -> Session:
    """Append template commands as steps to the session."""
    for cmd in template.commands:
        session = add_step(session, command=cmd, note=f"from template: {template.name}")
    for tag in template.tags:
        if tag not in session.tags:
            session.tags.append(tag)
    return session


def template_summary(template: Template) -> str:
    lines = [
        f"Template : {template.name}",
        f"Desc     : {template.description or '(none)'}",
        f"Commands : {len(template.commands)}",
        f"Tags     : {', '.join(template.tags) if template.tags else '(none)'}",
    ]
    return "\n".join(lines)
