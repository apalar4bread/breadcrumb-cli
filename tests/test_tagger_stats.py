import pytest
from breadcrumb.session import Session, add_step
from breadcrumb.tagger import add_tag
from breadcrumb.tagger_stats import compute_tag_stats, format_tag_stats


def make_session(name="s", tags=None):
    s = Session(name=name)
    if tags:
        for t in tags:
            add_tag(s, t)
    return s


def test_empty_sessions_returns_zero_stats():
    stats = compute_tag_stats([])
    assert stats.total_tags == 0
    assert stats.unique_tags == 0
    assert stats.sessions_with_tags == 0
    assert stats.sessions_without_tags == 0


def test_single_session_no_tags():
    stats = compute_tag_stats([make_session()])
    assert stats.total_tags == 0
    assert stats.sessions_without_tags == 1
    assert stats.sessions_with_tags == 0


def test_single_session_with_tags():
    s = make_session(tags=["deploy", "prod"])
    stats = compute_tag_stats([s])
    assert stats.total_tags == 2
    assert stats.unique_tags == 2
    assert stats.sessions_with_tags == 1
    assert stats.sessions_without_tags == 0


def test_tag_counts_are_correct():
    s1 = make_session(tags=["deploy", "prod"])
    s2 = make_session(tags=["deploy", "staging"])
    stats = compute_tag_stats([s1, s2])
    assert stats.tag_counts["deploy"] == 2
    assert stats.tag_counts["prod"] == 1
    assert stats.tag_counts["staging"] == 1


def test_most_common_returns_top_entries():
    s1 = make_session(tags=["a", "b", "c"])
    s2 = make_session(tags=["a", "b"])
    s3 = make_session(tags=["a"])
    stats = compute_tag_stats([s1, s2, s3])
    assert stats.most_common[0][0] == "a"
    assert stats.most_common[0][1] == 3


def test_tags_are_normalized_to_lowercase():
    s = make_session(tags=["Deploy", "PROD"])
    stats = compute_tag_stats([s])
    assert "deploy" in stats.tag_counts
    assert "prod" in stats.tag_counts


def test_format_tag_stats_contains_totals():
    s = make_session(tags=["ci", "cd"])
    stats = compute_tag_stats([s])
    out = format_tag_stats(stats)
    assert "Total tags" in out
    assert "Unique tags" in out
    assert "ci" in out or "cd" in out


def test_format_tag_stats_no_tags():
    stats = compute_tag_stats([])
    out = format_tag_stats(stats)
    assert "0" in out
