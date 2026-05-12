"""Tests for breadcrumb/recycler.py."""
import pytest

from breadcrumb.session import Session
from breadcrumb.recycler import (
    RecycleEntry,
    RecycleError,
    format_recycle_entry,
    format_recycle_list,
    recycle_session,
    restore_session,
)


def make_session(name="test", sid="abc-123") -> Session:
    s = Session(name=name)
    s.id = sid
    return s


def test_recycle_session_creates_entry():
    s = make_session()
    entry = recycle_session(s)
    assert isinstance(entry, RecycleEntry)
    assert entry.session is s


def test_recycle_session_stores_reason():
    s = make_session()
    entry = recycle_session(s, reason="  no longer needed  ")
    assert entry.reason == "no longer needed"


def test_recycle_session_no_id_raises():
    s = Session(name="x")
    s.id = ""
    with pytest.raises(RecycleError):
        recycle_session(s)


def test_recycle_entry_deleted_at_is_set():
    s = make_session()
    entry = recycle_session(s)
    assert entry.deleted_at != ""


def test_restore_session_returns_original():
    s = make_session()
    entry = recycle_session(s)
    restored = restore_session(entry)
    assert restored is s


def test_roundtrip_serialization():
    s = make_session()
    entry = recycle_session(s, reason="cleanup")
    data = entry.to_dict()
    recovered = RecycleEntry.from_dict(data)
    assert recovered.session.name == s.name
    assert recovered.reason == "cleanup"
    assert recovered.deleted_at == entry.deleted_at


def test_format_recycle_entry_contains_name():
    s = make_session(name="my-session")
    entry = recycle_session(s)
    text = format_recycle_entry(entry)
    assert "my-session" in text


def test_format_recycle_entry_shows_reason():
    s = make_session()
    entry = recycle_session(s, reason="old")
    text = format_recycle_entry(entry)
    assert "old" in text


def test_format_recycle_list_empty():
    text = format_recycle_list([])
    assert "empty" in text.lower()


def test_format_recycle_list_shows_names():
    entries = [recycle_session(make_session(name=f"s{i}", sid=f"id-{i}")) for i in range(3)]
    text = format_recycle_list(entries)
    assert "s0" in text
    assert "s2" in text
