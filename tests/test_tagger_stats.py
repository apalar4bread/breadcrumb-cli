import pytest
from breadcrumb.session import Session, Step
from breadcrumb.tagger_stats import compute_tag_stats, format_tag_stats, TagStats


def make_session(name: str, tags=None, commands=None) -> Session:
    s = Session(name=name)
    s.tags = tags or []
    for cmd in (commands or []):
        s.steps.append(Step(command=cmd))
    return s


def test_empty_sessions_returns_zero_stats():
    stats = compute_tag_stats([])
    assert stats.total_tags == 0
    assert stats.unique_tags == 0
    assert stats.sessions_with_tags == 0
    assert stats.tag_counts == {}


def test_single_session_no_tags():
    s = make_session("s1", tags=[])
    stats = compute_tag_stats([s])
    assert stats.total_tags == 0
    assert stats.sessions_with_tags == 0


def test_single_session_with_tags():
    s = make_session("s1", tags=["python", "devops"])
    stats = compute_tag_stats([s])
    assert stats.total_tags == 2
    assert stats.unique_tags == 2
    assert stats.sessions_with_tags == 1


def test_tag_counts_are_correct():
    s1 = make_session("s1", tags=["python", "devops"])
    s2 = make_session("s2", tags=["python", "cloud"])
    stats = compute_tag_stats([s1, s2])
    assert stats.tag_counts["python"] == 2
    assert stats.tag_counts["devops"] == 1
    assert stats.tag_counts["cloud"] == 1


def test_tag_normalization():
    s = make_session("s1", tags=["Python", "PYTHON", "python"])
    stats = compute_tag_stats([s])
    assert stats.unique_tags == 1
    assert stats.tag_counts["python"] == 3


def test_sessions_with_tags_count():
    s1 = make_session("s1", tags=["alpha"])
    s2 = make_session("s2", tags=[])
    s3 = make_session("s3", tags=["beta"])
    stats = compute_tag_stats([s1, s2, s3])
    assert stats.sessions_with_tags == 2


def test_format_tag_stats_contains_totals():
    stats = TagStats(total_tags=5, unique_tags=3, tag_counts={"a": 3, "b": 2}, sessions_with_tags=2)
    output = format_tag_stats(stats)
    assert "5" in output
    assert "3" in output
    assert "a" in output
    assert "b" in output


def test_format_tag_stats_no_tags():
    stats = TagStats()
    output = format_tag_stats(stats)
    assert "0" in output
