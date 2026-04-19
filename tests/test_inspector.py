import pytest
from breadcrumb.session import Session, Step
from breadcrumb.inspector import inspect_step, format_inspection, InspectError


def make_session(steps=None):
    s = Session(id="s1", name="Test")
    for step in (steps or []):
        s.steps.append(step)
    return s


def make_step(command="echo hi", note="a note", **meta):
    return Step(command=command, note=note, timestamp="2024-01-01T00:00:00", metadata=meta)


def test_inspect_basic_fields():
    session = make_session([make_step()])
    insp = inspect_step(session, 0)
    assert insp.command == "echo hi"
    assert insp.note == "a note"
    assert insp.index == 0


def test_inspect_tags():
    step = make_step(tags=["deploy", "prod"])
    session = make_session([step])
    insp = inspect_step(session, 0)
    assert insp.tags == ["deploy", "prod"]


def test_inspect_pinned_bookmarked():
    step = make_step(pinned=True, bookmarked=True)
    session = make_session([step])
    insp = inspect_step(session, 0)
    assert insp.pinned is True
    assert insp.bookmarked is True


def test_inspect_annotation():
    step = make_step(annotation="important step")
    session = make_session([step])
    insp = inspect_step(session, 0)
    assert insp.annotated is True
    assert insp.annotation == "important step"


def test_inspect_no_annotation():
    session = make_session([make_step()])
    insp = inspect_step(session, 0)
    assert insp.annotated is False
    assert insp.annotation is None


def test_inspect_extra_metadata():
    step = make_step(custom_key="custom_val")
    session = make_session([step])
    insp = inspect_step(session, 0)
    assert insp.extra.get("custom_key") == "custom_val"


def test_inspect_out_of_range():
    session = make_session([make_step()])
    with pytest.raises(InspectError):
        inspect_step(session, 5)


def test_inspect_empty_session():
    session = make_session([])
    with pytest.raises(InspectError):
        inspect_step(session, 0)


def test_format_inspection_contains_command():
    session = make_session([make_step()])
    insp = inspect_step(session, 0)
    output = format_inspection(insp)
    assert "echo hi" in output
    assert "Step #0" in output


def test_format_inspection_shows_none_for_missing():
    session = make_session([make_step()])
    insp = inspect_step(session, 0)
    output = format_inspection(insp)
    assert "(none)" in output
