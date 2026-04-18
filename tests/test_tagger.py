"""Tests for breadcrumb.tagger module."""
import pytest
from unittest.mock import MagicMock
from breadcrumb.session import Session
from breadcrumb.tagger import add_tag, remove_tag, list_tags, find_by_tag


@pytest.fixture
def session():
    return Session(name="test-session")


def test_add_tag(session):
    result = add_tag(session, "deploy")
    assert "deploy" in result.tags


def test_add_tag_normalizes_case(session):
    add_tag(session, "Deploy")
    assert "deploy" in session.tags


def test_add_tag_no_duplicates(session):
    add_tag(session, "deploy")
    add_tag(session, "deploy")
    assert session.tags.count("deploy") == 1


def test_add_tag_empty_raises(session):
    with pytest.raises(ValueError, match="empty"):
        add_tag(session, "  ")


def test_remove_tag(session):
    session.tags = ["deploy", "prod"]
    remove_tag(session, "deploy")
    assert "deploy" not in session.tags
    assert "prod" in session.tags


def test_remove_tag_not_present(session):
    session.tags = ["prod"]
    remove_tag(session, "missing")  # should not raise
    assert session.tags == ["prod"]


def test_list_tags_sorted(session):
    session.tags = ["zebra", "alpha", "beta"]
    assert list_tags(session) == ["alpha", "beta", "zebra"]


def test_find_by_tag():
    store = MagicMock()
    s1 = Session(name="s1", tags=["deploy"])
    s2 = Session(name="s2", tags=["test"])
    s3 = Session(name="s3", tags=["deploy", "prod"])
    store.list_sessions.return_value = ["s1", "s2", "s3"]
    store.load.side_effect = lambda name: {"s1": s1, "s2": s2, "s3": s3}[name]
    results = find_by_tag(store, "deploy")
    assert len(results) == 2
    assert s1 in results
    assert s3 in results
