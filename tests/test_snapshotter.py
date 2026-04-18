import pytest
from breadcrumb.session import Session, Step
from breadcrumb.snapshotter import take_snapshot, restore_snapshot, SnapshotError, Snapshot


def make_session(n_steps=3):
    s = Session(id="s1", name="test")
    for i in range(n_steps):
        s.steps.append(Step(command=f"echo {i}", note=f"step {i}"))
    return s


def test_take_snapshot_all_steps():
    s = make_session(3)
    snap = take_snapshot(s)
    assert len(snap.steps) == 3
    assert snap.step_index == 2
    assert snap.session_id == "s1"


def test_take_snapshot_up_to():
    s = make_session(4)
    snap = take_snapshot(s, up_to=1)
    assert len(snap.steps) == 2
    assert snap.steps[-1].command == "echo 1"


def test_take_snapshot_empty_raises():
    s = Session(id="s1", name="empty")
    with pytest.raises(SnapshotError, match="no steps"):
        take_snapshot(s)


def test_take_snapshot_out_of_range():
    s = make_session(2)
    with pytest.raises(SnapshotError, match="out of range"):
        take_snapshot(s, up_to=5)


def test_snapshot_roundtrip():
    s = make_session(3)
    snap = take_snapshot(s)
    d = snap.to_dict()
    snap2 = Snapshot.from_dict(d)
    assert snap2.session_id == snap.session_id
    assert len(snap2.steps) == len(snap.steps)
    assert snap2.steps[0].command == snap.steps[0].command


def test_restore_snapshot_replaces_steps():
    s = make_session(4)
    snap = take_snapshot(s, up_to=1)
    restored = restore_snapshot(snap, s)
    assert len(restored.steps) == 2
    assert restored.id == s.id
    # original untouched
    assert len(s.steps) == 4
