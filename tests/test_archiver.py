import json
import pytest
from pathlib import Path
from breadcrumb.session import Session, add_step
from breadcrumb.archiver import export_archive, import_archive, archive_summary, ArchiveError


def make_session(name="test") -> Session:
    s = Session(name=name)
    add_step(s, "echo hello", note="greet")
    add_step(s, "ls -la")
    return s


def test_export_creates_file(tmp_path):
    out = tmp_path / "archive.json"
    sessions = [make_session("s1"), make_session("s2")]
    result = export_archive(sessions, str(out))
    assert result.exists()
    data = json.loads(out.read_text())
    assert data["breadcrumb_archive"] is True
    assert len(data["sessions"]) == 2


def test_export_wrong_extension_raises(tmp_path):
    with pytest.raises(ArchiveError, match=".json"):
        export_archive([], str(tmp_path / "archive.zip"))


def test_import_roundtrip(tmp_path):
    out = tmp_path / "archive.json"
    original = [make_session("alpha"), make_session("beta")]
    export_archive(original, str(out))
    loaded = import_archive(str(out))
    assert len(loaded) == 2
    names = {s.name for s in loaded}
    assert names == {"alpha", "beta"}


def test_import_preserves_steps(tmp_path):
    out = tmp_path / "archive.json"
    s = make_session("with-steps")
    export_archive([s], str(out))
    [restored] = import_archive(str(out))
    assert len(restored.steps) == 2
    assert restored.steps[0].command == "echo hello"
    assert restored.steps[0].note == "greet"


def test_import_missing_file_raises():
    with pytest.raises(ArchiveError, match="not found"):
        import_archive("/nonexistent/archive.json")


def test_import_invalid_json_raises(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("not json at all")
    with pytest.raises(ArchiveError, match="Invalid JSON"):
        import_archive(str(bad))


def test_import_wrong_format_raises(tmp_path):
    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"hello": "world"}))
    with pytest.raises(ArchiveError, match="breadcrumb archive"):
        import_archive(str(wrong))


def test_archive_summary(tmp_path):
    out = tmp_path / "archive.json"
    sessions = [make_session("x"), make_session("y")]
    export_archive(sessions, str(out))
    info = archive_summary(str(out))
    assert info["session_count"] == 2
    assert info["total_steps"] == 4
    assert set(info["session_names"]) == {"x", "y"}
