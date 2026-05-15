"""Tests for breadcrumb.badge."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.badge import award_badges, format_badge_result, BadgeError


def make_session(name="test", steps=None, tags=None) -> Session:
    s = Session(id="sess-1", name=name)
    s.tags = tags or []
    s.steps = steps or []
    return s


def make_step(command="echo hi", note="", metadata=None) -> Step:
    return Step(command=command, note=note, metadata=metadata or {})


def test_no_steps_earns_no_badges():
    session = make_session(steps=[])
    result = award_badges(session)
    assert result.badges == []
    assert result.count == 0


def test_first_step_badge():
    session = make_session(steps=[make_step()])
    result = award_badges(session)
    assert "first_step" in result.badges


def test_five_steps_badge():
    session = make_session(steps=[make_step() for _ in range(5)])
    result = award_badges(session)
    assert "five_steps" in result.badges
    assert "first_step" in result.badges


def test_ten_steps_badge():
    session = make_session(steps=[make_step() for _ in range(10)])
    result = award_badges(session)
    assert "ten_steps" in result.badges


def test_tagged_badge():
    session = make_session(steps=[make_step()], tags=["devops"])
    result = award_badges(session)
    assert "tagged" in result.badges


def test_no_tagged_badge_when_no_tags():
    session = make_session(steps=[make_step()], tags=[])
    result = award_badges(session)
    assert "tagged" not in result.badges


def test_noted_badge_all_steps_have_notes():
    steps = [make_step(note="a note"), make_step(note="another")]
    session = make_session(steps=steps)
    result = award_badges(session)
    assert "noted" in result.badges


def test_noted_badge_missing_when_step_has_no_note():
    steps = [make_step(note="a note"), make_step(note="")]
    session = make_session(steps=steps)
    result = award_badges(session)
    assert "noted" not in result.badges


def test_pinned_badge():
    steps = [make_step(metadata={"pinned": True})]
    session = make_session(steps=steps)
    result = award_badges(session)
    assert "pinned" in result.badges


def test_bookmarked_badge():
    steps = [make_step(metadata={"bookmarked": True})]
    session = make_session(steps=steps)
    result = award_badges(session)
    assert "bookmarked" in result.badges


def test_missing_id_raises():
    session = make_session()
    session.id = ""
    with pytest.raises(BadgeError):
        award_badges(session)


def test_summary_no_badges():
    session = make_session(steps=[])
    result = award_badges(session)
    assert "no badges" in result.summary()


def test_summary_with_badges():
    session = make_session(steps=[make_step()])
    result = award_badges(session)
    assert "first_step" in result.summary()


def test_format_badge_result_contains_badge_name():
    session = make_session(steps=[make_step()], tags=["ci"])
    result = award_badges(session)
    formatted = format_badge_result(result)
    assert "first_step" in formatted
    assert "tagged" in formatted


def test_format_badge_result_no_badges_shows_none():
    session = make_session(steps=[])
    result = award_badges(session)
    formatted = format_badge_result(result)
    assert "(none)" in formatted
