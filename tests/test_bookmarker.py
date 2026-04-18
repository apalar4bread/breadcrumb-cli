import pytest
from breadcrumb.session import Session, Step
from breadcrumb.bookmarker import (
    bookmark_step, unbookmark_step, is_bookmarked, list_bookmarked, BookmarkError
)


def make_session():
    s = Session(name="test")
    s.steps = [
        Step(command="echo hello"),
        Step(command="ls -la"),
        Step(command="pwd"),
    ]
    return s


def test_bookmark_step_sets_metadata():
    s = make_session()
    bookmark_step(s, 1)
    assert s.steps[1].metadata.get("bookmarked") is True


def test_bookmark_does_not_affect_others():
    s = make_session()
    bookmark_step(s, 0)
    assert not s.steps[1].metadata.get("bookmarked")
    assert not s.steps[2].metadata.get("bookmarked")


def test_unbookmark_removes_flag():
    s = make_session()
    bookmark_step(s, 2)
    unbookmark_step(s, 2)
    assert not s.steps[2].metadata.get("bookmarked")


def test_unbookmark_no_error_if_not_bookmarked():
    s = make_session()
    unbookmark_step(s, 0)  # should not raise


def test_is_bookmarked_true():
    s = make_session()
    bookmark_step(s, 1)
    assert is_bookmarked(s, 1) is True


def test_is_bookmarked_false():
    s = make_session()
    assert is_bookmarked(s, 0) is False


def test_list_bookmarked_returns_correct_indices():
    s = make_session()
    bookmark_step(s, 0)
    bookmark_step(s, 2)
    result = list_bookmarked(s)
    assert [i for i, _ in result] == [0, 2]


def test_list_bookmarked_empty():
    s = make_session()
    assert list_bookmarked(s) == []


def test_bookmark_out_of_range_raises():
    s = make_session()
    with pytest.raises(BookmarkError):
        bookmark_step(s, 10)


def test_unbookmark_out_of_range_raises():
    s = make_session()
    with pytest.raises(BookmarkError):
        unbookmark_step(s, -5)


def test_is_bookmarked_out_of_range_raises():
    s = make_session()
    with pytest.raises(BookmarkError):
        is_bookmarked(s, 99)
