import pytest
from breadcrumb.session import Session, add_step
from breadcrumb.tagger import add_tag
from breadcrumb.tagger_stats import compute_tag_stats, format_tag_stats, TagStats


def make_session(name: str = "s") -> Session:
    return Session(id=name, name=name)


def test_empty_sessions_returns_zero_stats():
    stats = compute_tag_stats([])
    assert stats.total_tags == 0
    assert stats.unique_tags == 0
    assert stats.sessions_with_tags == 0
    assert stats.sessions_without_tags == 0


def test_single_session_no_tags():
    s = make_session()
    stats = compute_tag_stats([s])
    assert stats.total_tags == 0
    assert stats.sessions_without_tags == 1
    assert stats.sessions_with_tags == 0


def test_single_session_with_tags():
    s = make_session()
    add_tag(s, "alpha")
    add_tag(s, "beta")
    stats = compute_tag_stats([s])
    assert stats.total_tags == 2
    assert stats.unique_tags == 2
    assert stats.sessions_with_tags == 1
    assert stats.sessions_without_tags == 0


def test_tag_counts_are_correct():
    s1 = make_session("a")
    s2 = make_session("b")
    add_tag(s1, "deploy")
    add_tag(s2, "deploy")
    add_tag(s2, "infra")
    stats = compute_tag_stats([s1, s2])
    assert stats.tag_counts["deploy"] == 2
    assert stats.tag_counts["infra"] == 1


def test_tag_normalizes_to_lowercase():
    s = make_session()
    add_tag(s, "CI")
    stats = compute_tag_stats([s])
    assert "ci" in stats.tag_counts


def test_most_common_limited_to_five():
    sessions = []
    for i in range(8):
        s = make_session(str(i))
        add_tag(s, f"tag{i}")
        sessions.append(s)
    stats = compute_tag_stats(sessions)
    assert len(stats.most_common) <= 5


def test_format_tag_stats_contains_totals():
    s = make_session()
    add_tag(s, "ops")
    stats = compute_tag_stats([s])
    output = format_tag_stats(stats)
    assert "Total tag usages" in output
    assert "Unique tags" in output


def test_format_tag_stats_lists_top_tags():
    s = make_session()
    add_tag(s, "deploy")
    stats = compute_tag_stats([s])
    output = format_tag_stats(stats)
    assert "deploy" in output


def test_multiple_sessions_without_tags():
    sessions = [make_session(str(i)) for i in range(4)]
    stats = compute_tag_stats(sessions)
    assert stats.sessions_without_tags == 4
    assert stats.sessions_with_tags == 0
