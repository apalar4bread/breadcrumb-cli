import pytest
from datetime import datetime, timedelta
from breadcrumb.session import Session, Step
from breadcrumb.filterer import (
    filter_by_command,
    filter_by_note,
    filter_by_metadata_key,
    filter_by_date_range,
    FilterError,
)


def make_session():
    s = Session(name="test")
    s.steps = [
        Step(command="git commit -m 'init'", note="first commit", metadata={"pinned": True}),
        Step(command="git push origin main", note="push", metadata={}),
        Step(command="docker build .", note=None, metadata={"label": "build"}),
        Step(command="docker run app", note="run container", metadata={}),
    ]
    return s


@pytest.fixture
def session():
    return make_session()


def test_filter_by_command_found(session):
    results = filter_by_command(session, "git")
    assert len(results) == 2


def test_filter_by_command_case_insensitive(session):
    results = filter_by_command(session, "DOCKER")
    assert len(results) == 2


def test_filter_by_command_case_sensitive_no_match(session):
    results = filter_by_command(session, "DOCKER", case_sensitive=True)
    assert results == []


def test_filter_by_command_not_found(session):
    results = filter_by_command(session, "kubectl")
    assert results == []


def test_filter_by_command_empty_raises(session):
    with pytest.raises(FilterError):
        filter_by_command(session, "  ")


def test_filter_by_note_found(session):
    results = filter_by_note(session, "commit")
    assert len(results) == 1
    assert results[0].note == "first commit"


def test_filter_by_note_skips_none(session):
    results = filter_by_note(session, "build")
    assert results == []


def test_filter_by_note_empty_raises(session):
    with pytest.raises(FilterError):
        filter_by_note(session, "")


def test_filter_by_metadata_key_found(session):
    results = filter_by_metadata_key(session, "pinned")
    assert len(results) == 1


def test_filter_by_metadata_key_not_found(session):
    results = filter_by_metadata_key(session, "nonexistent")
    assert results == []


def test_filter_by_metadata_key_empty_raises(session):
    with pytest.raises(FilterError):
        filter_by_metadata_key(session, "")


def test_filter_by_date_range_all(session):
    results = filter_by_date_range(session)
    assert len(results) == 4


def test_filter_by_date_range_future_start(session):
    future = datetime.utcnow() + timedelta(days=1)
    results = filter_by_date_range(session, start=future)
    assert results == []


def test_filter_by_date_range_past_end(session):
    past = datetime.utcnow() - timedelta(days=1)
    results = filter_by_date_range(session, end=past)
    assert results == []
