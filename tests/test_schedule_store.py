import pytest
from breadcrumb.scheduler import set_schedule, ScheduleError
from breadcrumb.schedule_store import ScheduleStore


@pytest.fixture
def store(tmp_path):
    return ScheduleStore(base_dir=str(tmp_path / "schedules"))


def test_save_and_load(store):
    s = set_schedule("sess-1", "daily", notes="hi")
    store.save(s)
    loaded = store.load("sess-1")
    assert loaded.session_id == "sess-1"
    assert loaded.interval == "daily"
    assert loaded.notes == "hi"


def test_load_missing_raises(store):
    with pytest.raises(ScheduleError, match="No schedule found"):
        store.load("ghost")


def test_delete_schedule(store):
    s = set_schedule("sess-2", "hourly")
    store.save(s)
    store.delete("sess-2")
    with pytest.raises(ScheduleError):
        store.load("sess-2")


def test_delete_missing_raises(store):
    with pytest.raises(ScheduleError):
        store.delete("nope")


def test_list_schedules(store):
    store.save(set_schedule("a", "daily"))
    store.save(set_schedule("b", "weekly"))
    schedules = store.list_schedules()
    ids = [s.session_id for s in schedules]
    assert "a" in ids
    assert "b" in ids


def test_list_empty(store):
    assert store.list_schedules() == []
