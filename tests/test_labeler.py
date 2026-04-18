import pytest
from breadcrumb.session import Session, Step
from breadcrumb.labeler import (
    set_label, clear_label, get_label, find_by_label, LabelError, VALID_LABELS
)


def make_session():
    s = Session(name="test")
    s.steps = [
        Step(command="echo hello"),
        Step(command="ls -la"),
        Step(command="pwd"),
    ]
    return s


def test_set_label_valid():
    s = make_session()
    set_label(s, 0, "high")
    assert s.steps[0].metadata["label"] == "high"


def test_set_label_normalizes_case():
    s = make_session()
    set_label(s, 1, "  TODO  ")
    assert s.steps[1].metadata["label"] == "todo"


def test_set_label_invalid_raises():
    s = make_session()
    with pytest.raises(LabelError, match="Invalid label"):
        set_label(s, 0, "urgent")


def test_set_label_empty_raises():
    s = make_session()
    with pytest.raises(LabelError, match="empty"):
        set_label(s, 0, "   ")


def test_set_label_out_of_range_raises():
    s = make_session()
    with pytest.raises(LabelError, match="out of range"):
        set_label(s, 10, "low")


def test_clear_label_removes_it():
    s = make_session()
    set_label(s, 0, "done")
    clear_label(s, 0)
    assert "label" not in s.steps[0].metadata


def test_clear_label_no_error_if_absent():
    s = make_session()
    clear_label(s, 0)  # should not raise


def test_get_label_returns_value():
    s = make_session()
    set_label(s, 2, "skip")
    assert get_label(s, 2) == "skip"


def test_get_label_returns_none_if_unset():
    s = make_session()
    assert get_label(s, 0) is None


def test_find_by_label_returns_matches():
    s = make_session()
    set_label(s, 0, "todo")
    set_label(s, 2, "todo")
    results = find_by_label(s, "todo")
    assert [i for i, _ in results] == [0, 2]


def test_find_by_label_empty_if_none():
    s = make_session()
    assert find_by_label(s, "critical") == []
