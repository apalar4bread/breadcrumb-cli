import pytest
from pathlib import Path
from breadcrumb.session import Session, Step
from breadcrumb.snapshotter import take_snapshot
from breadcrumb.snapshot_store import SnapshotStore


@pytest.fixture
def store(tmp_path):
    return SnapshotStore(tmp_path / "snapshots")


def make_snap(session_id="s1", n=3):
    s = Session(id=session_id, name="demo")
    for i in range(n):
        s.steps.append(Step(command=f"cmd {i}"))
    return take_snapshot(s)


def test_save_and_load(store):
    snap = make_snap()
    store.save(snap, "v1")
    loaded = store.load("s1", "v1")
    assert loaded.session_id == "s1"
    assert len(loaded.steps) == 3


def test_load_missing_raises(store):
    with pytest.raises(FileNotFoundError):
        store.load("s1", "ghost")


def test_list_snapshots(store):
    store.save(make_snap("s1"), "alpha")
    store.save(make_snap("s1"), "beta")
    store.save(make_snap("s2"), "other")
    labels = store.list_snapshots("s1")
    assert set(labels) == {"alpha", "beta"}


def test_list_snapshots_empty(store):
    """list_snapshots should return an empty list for unknown session ids."""
    assert store.list_snapshots("nonexistent") == []


def test_delete_snapshot(store):
    store.save(make_snap(), "v1")
    assert store.delete("s1", "v1") is True
    assert store.list_snapshots("s1") == []


def test_delete_missing_returns_false(store):
    assert store.delete("s1", "nope") is False


def test_overwrite_snapshot(store):
    """Saving with the same label should overwrite the previous snapshot."""
    store.save(make_snap("s1", n=2), "v1")
    store.save(make_snap("s1", n=5), "v1")
    loaded = store.load("s1", "v1")
    assert len(loaded.steps) == 5
    # label should still appear only once
    assert store.list_snapshots("s1").count("v1") == 1
