import pytest
from breadcrumb.session import Session
from breadcrumb.summarizer import summarize_session, summarize_all, format_summary


@pytest.fixture
def simple_session():
    s = Session(name="deploy")
    s.add_step("git pull", note="fetch latest")
    s.add_step("make build")
    s.add_step("make build")
    s.add_step("./deploy.sh", note="run deploy")
    return s


def test_summarize_step_count(simple_session):
    summary = summarize_session(simple_session)
    assert summary["step_count"] == 4


def test_summarize_unique_commands(simple_session):
    summary = summarize_session(simple_session)
    assert summary["unique_commands"] == 3  # git pull, make build, ./deploy.sh


def test_summarize_most_common_command(simple_session):
    summary = summarize_session(simple_session)
    cmd, count = summary["most_common_command"]
    assert cmd == "make build"
    assert count == 2


def test_summarize_notes_count(simple_session):
    summary = summarize_session(simple_session)
    assert summary["notes_count"] == 2


def test_summarize_empty_session():
    s = Session(name="empty")
    summary = summarize_session(s)
    assert summary["step_count"] == 0
    assert summary["most_common_command"] is None
    assert summary["notes_count"] == 0


def test_summarize_all():
    s1 = Session(name="a")
    s1.add_step("echo hi")
    s2 = Session(name="b")
    s2.add_step("ls")
    results = summarize_all([s1, s2])
    assert len(results) == 2
    assert results[0]["name"] == "a"
    assert results[1]["name"] == "b"


def test_format_summary_contains_name(simple_session):
    summary = summarize_session(simple_session)
    output = format_summary(summary)
    assert "deploy" in output
    assert "Steps" in output
    assert "make build" in output
