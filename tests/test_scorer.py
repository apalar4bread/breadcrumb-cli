import pytest
from breadcrumb.session import Session, Step
from breadcrumb.scorer import score_step, score_session, top_steps, format_session_score
import uuid


def make_step(command="echo hi", note="", **meta):
    return Step(command=command, note=note, metadata=meta)


def make_session(steps=None, tags=None):
    return Session(
        id=str(uuid.uuid4()),
        name="test",
        steps=steps or [],
        tags=tags or [],
    )


def test_score_step_bare_command():
    s = score_step(make_step(command="ls"), 0)
    assert s.score == 1.0
    assert "has command" in s.reasons


def test_score_step_with_note():
    s = score_step(make_step(note="list files"), 0)
    assert "has note" in s.reasons
    assert s.score >= 3.0


def test_score_step_pinned():
    s = score_step(make_step(pinned=True), 0)
    assert "pinned" in s.reasons
    assert s.score >= 4.0


def test_score_step_bookmarked():
    s = score_step(make_step(bookmarked=True), 0)
    assert "bookmarked" in s.reasons


def test_score_step_annotated():
    s = score_step(make_step(annotation="important"), 0)
    assert "annotated" in s.reasons


def test_score_step_labeled():
    s = score_step(make_step(label="setup"), 0)
    assert "labeled" in s.reasons


def test_score_session_sums_steps():
    steps = [make_step(note="a"), make_step(), make_step(pinned=True)]
    session = make_session(steps=steps)
    result = score_session(session)
    assert result.total_score > 0
    assert len(result.step_scores) == 3


def test_score_session_tags_add_score():
    session = make_session(steps=[make_step()], tags=["deploy", "ci"])
    result = score_session(session)
    assert result.total_score >= 2.0


def test_top_steps_returns_n():
    steps = [make_step(note=f"note {i}") for i in range(10)]
    session = make_session(steps=steps)
    top = top_steps(session, n=3)
    assert len(top) == 3


def test_top_steps_sorted_descending():
    steps = [make_step(), make_step(pinned=True, note="hi"), make_step(note="x")]
    session = make_session(steps=steps)
    top = top_steps(session)
    scores = [s.score for s in top]
    assert scores == sorted(scores, reverse=True)


def test_format_session_score_contains_name():
    session = make_session(steps=[make_step()])
    result = score_session(session)
    output = format_session_score(result)
    assert "test" in output
    assert "score" in output
