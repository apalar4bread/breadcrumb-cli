import pytest
from breadcrumb.session import Session, Step
from breadcrumb.annotator import (
    annotate_step, clear_annotation, get_annotation,
    list_annotated, AnnotateError
)


def make_session():
    s = Session(name="test")
    s.steps = [
        Step(command="echo hello"),
        Step(command="ls -la"),
        Step(command="pwd"),
    ]
    return s


def test_annotate_step_sets_comment():
    s = make_session()
    annotate_step(s, 0, "prints hello")
    assert s.steps[0].metadata["comment"] == "prints hello"


def test_annotate_step_strips_whitespace():
    s = make_session()
    annotate_step(s, 1, "  list files  ")
    assert s.steps[1].metadata["comment"] == "list files"


def test_annotate_step_replaces_existing():
    s = make_session()
    annotate_step(s, 0, "first")
    annotate_step(s, 0, "second")
    assert s.steps[0].metadata["comment"] == "second"


def test_annotate_step_empty_raises():
    s = make_session()
    with pytest.raises(AnnotateError):
        annotate_step(s, 0, "")


def test_annotate_step_blank_raises():
    s = make_session()
    with pytest.raises(AnnotateError):
        annotate_step(s, 0, "   ")


def test_annotate_step_out_of_range_raises():
    s = make_session()
    with pytest.raises(AnnotateError):
        annotate_step(s, 10, "oops")


def test_annotate_step_negative_index_raises():
    s = make_session()
    with pytest.raises(AnnotateError):
        annotate_step(s, -1, "negative")


def test_clear_annotation_removes_comment():
    s = make_session()
    annotate_step(s, 0, "some note")
    clear_annotation(s, 0)
    assert "comment" not in s.steps[0].metadata


def test_clear_annotation_no_error_if_missing():
    s = make_session()
    clear_annotation(s, 0)  # should not raise


def test_clear_annotation_out_of_range_raises():
    s = make_session()
    with pytest.raises(AnnotateError):
        clear_annotation(s, 99)


def test_get_annotation_returns_none_if_missing():
    s = make_session()
    assert get_annotation(s.steps[0]) is None


def test_get_annotation_returns_comment():
    s = make_session()
    annotate_step(s, 2, "current dir")
    assert get_annotation(s.steps[2]) == "current dir"


def test_list_annotated_empty():
    s = make_session()
    assert list_annotated(s) == []


def test_list_annotated_returns_correct_indices():
    s = make_session()
    annotate_step(s, 0, "first")
    annotate_step(s, 2, "third")
    result = list_annotated(s)
    assert [i for i, _ in result] == [0, 2]


def test_list_annotated_returns_correct_comments():
    s = make_session()
    annotate_step(s, 0, "first")
    annotate_step(s, 2, "third")
    result = list_annotated(s)
    assert [comment for _, comment in result] == ["first", "third"]
