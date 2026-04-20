"""Tests for breadcrumb/linker.py"""

import pytest
from breadcrumb.session import Session
from breadcrumb.linker import (
    add_link,
    remove_link,
    list_links,
    format_links,
    LinkError,
    LINK_TYPES,
)


def make_session(name="test-session", sid="sess-abc") -> Session:
    s = Session(name=name)
    s.id = sid
    return s


def test_add_link_basic():
    s = make_session(sid="aaa")
    link = add_link(s, target_id="bbb", link_type="follows")
    assert link.source_id == "aaa"
    assert link.target_id == "bbb"
    assert link.link_type == "follows"
    assert link.note is None


def test_add_link_with_note():
    s = make_session(sid="aaa")
    link = add_link(s, target_id="bbb", link_type="related", note="  context  ")
    assert link.note == "context"


def test_add_link_normalizes_type():
    s = make_session(sid="aaa")
    link = add_link(s, target_id="bbb", link_type="DEPENDS-ON")
    assert link.link_type == "depends-on"


def test_add_link_invalid_type_raises():
    s = make_session()
    with pytest.raises(LinkError, match="Invalid link type"):
        add_link(s, target_id="bbb", link_type="owns")


def test_add_link_empty_target_raises():
    s = make_session()
    with pytest.raises(LinkError, match="target_id"):
        add_link(s, target_id="  ", link_type="follows")


def test_add_link_self_link_raises():
    s = make_session(sid="aaa")
    with pytest.raises(LinkError, match="itself"):
        add_link(s, target_id="aaa", link_type="follows")


def test_add_link_duplicate_raises():
    s = make_session(sid="aaa")
    add_link(s, target_id="bbb", link_type="blocks")
    with pytest.raises(LinkError, match="already exists"):
        add_link(s, target_id="bbb", link_type="blocks")


def test_add_link_different_types_allowed():
    s = make_session(sid="aaa")
    add_link(s, target_id="bbb", link_type="blocks")
    add_link(s, target_id="bbb", link_type="related")  # different type — ok
    assert len(list_links(s)) == 2


def test_remove_link_basic():
    s = make_session(sid="aaa")
    add_link(s, target_id="bbb", link_type="follows")
    remove_link(s, target_id="bbb", link_type="follows")
    assert list_links(s) == []


def test_remove_link_not_found_raises():
    s = make_session()
    with pytest.raises(LinkError, match="No"):
        remove_link(s, target_id="bbb", link_type="follows")


def test_list_links_empty():
    s = make_session()
    assert list_links(s) == []


def test_list_links_roundtrip():
    s = make_session(sid="aaa")
    add_link(s, target_id="bbb", link_type="depends-on", note="needs it")
    links = list_links(s)
    assert len(links) == 1
    assert links[0].note == "needs it"


def test_format_links_empty():
    assert format_links([]) == "No links."


def test_format_links_shows_type_and_target():
    s = make_session(sid="aaa")
    add_link(s, target_id="bbb", link_type="related", note="see also")
    output = format_links(list_links(s))
    assert "related" in output
    assert "bbb" in output
    assert "see also" in output


def test_all_valid_link_types_accepted():
    for i, lt in enumerate(LINK_TYPES):
        s = make_session(sid=f"src-{i}")
        link = add_link(s, target_id=f"tgt-{i}", link_type=lt)
        assert link.link_type == lt
