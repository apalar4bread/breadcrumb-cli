"""Score steps and sessions based on usage patterns and metadata richness."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List
from breadcrumb.session import Session, Step


@dataclass
class StepScore:
    step_index: int
    command: str
    score: float
    reasons: List[str]


@dataclass
class SessionScore:
    session_id: str
    session_name: str
    total_score: float
    step_scores: List[StepScore]


def score_step(step: Step, index: int) -> StepScore:
    score = 0.0
    reasons = []

    if step.command.strip():
        score += 1.0
        reasons.append("has command")

    if step.note:
        score += 2.0
        reasons.append("has note")

    if step.metadata.get("pinned"):
        score += 3.0
        reasons.append("pinned")

    if step.metadata.get("bookmarked"):
        score += 2.5
        reasons.append("bookmarked")

    if step.metadata.get("annotation"):
        score += 1.5
        reasons.append("annotated")

    if step.metadata.get("label"):
        score += 1.0
        reasons.append("labeled")

    return StepScore(step_index=index, command=step.command, score=score, reasons=reasons)


def score_session(session: Session) -> SessionScore:
    step_scores = [score_step(s, i) for i, s in enumerate(session.steps)]
    total = sum(ss.score for ss in step_scores)

    if session.tags:
        total += len(session.tags) * 0.5

    return SessionScore(
        session_id=session.id,
        session_name=session.name,
        total_score=round(total, 2),
        step_scores=step_scores,
    )


def top_steps(session: Session, n: int = 5) -> List[StepScore]:
    scores = [score_step(s, i) for i, s in enumerate(session.steps)]
    return sorted(scores, key=lambda x: x.score, reverse=True)[:n]


def format_session_score(ss: SessionScore) -> str:
    lines = [f"Session: {ss.session_name} (score: {ss.total_score})"]
    for s in ss.step_scores:
        tag_str = ", ".join(s.reasons) if s.reasons else "none"
        lines.append(f"  [{s.step_index}] {s.command!r:30s} score={s.score} ({tag_str})")
    return "\n".join(lines)
