"""Tests for breadcrumb/recycle_store.py."""
import pytest

from breadcrumb.session import Session
from breadcrumb.recycler import recycle_session
from breadcrumb.recycle_store import RecycleStore


@pytest.fixture
def store(tmp_path):
    return RecycleStore(base_dir=str(tmp_path / "recycle"))


def make_session(name="demo", sid="s-001") -> Session:
    s = Session(name=name)
    s.id = sid
    return s


def test_save_and_load(store):
    s = make_session()
    entry = recycle_session(s, reason="test")
    store.save(entry)
    loaded = store.load(s.id)
    assert loaded.session.name == s.name
    assert loaded.reason == "test"


def test_load_missing_raises(store):
    with pytest.raises(FileNotFoundError):
        store.load("nonexistent-id")


def test_list_entries_empty(store):
    assert store.list_entries() == []


def test_list_entries_returns_all(store):
    for i in range(3):
        s = make_session(name=f"s{i}", sid=f"id-{i}")
        store.save(recycle_session(s))
    entries = store.list_entries()
    assert len(entries) == 3


def test_delete_removes_entry(store):
    s = make_session()
    store.save(recycle_session(s))
    store.delete(s.id)
    with pytest.raises(FileNotFoundError):
        store.load(s.id)


def test_delete_missing_raises(store):
    with pytest.raises(FileNotFoundError):
        store.delete("ghost-id")


def test_purge_removes_all(store):
    for i in range(4):
        s = make_session(name=f"x{i}", sid=f"p-{i}")
        store.save(recycle_session(s))
    count = store.purge()
    assert count == 4
    assert store.list_entries() == []
