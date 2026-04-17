"""Core session tracking module for breadcrumb-cli."""

import os
import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Optional


@dataclass
class Step:
    command: str
    timestamp: float
    cwd: str
    exit_code: Optional[int] = None
    note: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class Session:
    name: str
    created_at: float = field(default_factory=time.time)
    steps: List[Step] = field(default_factory=list)

    def add_step(self, command: str, cwd: Optional[str] = None, exit_code: Optional[int] = None, note: Optional[str] = None):
        step = Step(
            command=command,
            timestamp=time.time(),
            cwd=cwd or os.getcwd(),
            exit_code=exit_code,
            note=note,
        )
        self.steps.append(step)
        return step

    def to_dict(self):
        return {
            "name": self.name,
            "created_at": self.created_at,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict):
        steps = [Step.from_dict(s) for s in data.get("steps", [])]
        return cls(name=data["name"], created_at=data["created_at"], steps=steps)
