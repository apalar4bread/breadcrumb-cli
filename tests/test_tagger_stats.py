"""Tests for breadcrumb.tagger_stats."""
import pytest

from breadcrumb.session import Session
from breadcrumb.tagger_stats import TagStats, compute_tag_stats, format_tag_stats


def make_session(name: str, tags=None) -> Session:
    s = Session(name=name)
    if tags is not None:
        s.metadata["tags"] = tags
    return s


def test_empty_sessions_returns_zero_stats():
    stats = compute_tag_stats([])
    assert stats.total_tags == 0
    assert stats.unique_tags == 0
    assert stats.tag_counts == {}
    assert stats.most_common == []
    assert stats.sessions_with_tags == 0
    assert stats.sessions_without_tags == 0


def test_single_session_no_tags():
    stats = compute_tag_stats([make_session("s1")])
    assert stats.sessions_without_tags == 1
    assert stats.sessions_with_tags == 0
    assert stats.total_tags == 0


def test_single_session_with_tags():
    stats = compute_tag_stats([make_session("s1", tags=["deploy", "infra"])])
    assert stats.sessions_with_tags == 1
    assert stats.sessions_without_tags == 0
    assert stats.total_tags == 2
    assert stats.unique_tags == 2


def test_tag_counts_are_correct():
    sessions = [
        make_session("s1", tags=["deploy", "infra"]),
        make_session("s2", tags=["deploy"]),
        make_session("s3", tags=["test"]),
    ]
    stats = compute_tag_stats(sessions)
    assert stats.tag_counts["deploy"] == 2
    assert stats.tag_counts["infra"] == 1
    assert stats.tag_counts["test"] == 1


def test_tags_are_normalized_to_lowercase():
    stats = compute_tag_stats([make_session("s1", tags=["Deploy", "DEPLOY"])])
    assert stats.unique_tags == 1
    assert stats.tag_counts["deploy"] == 2


def test_most_common_returns_up_to_five():
    sessions = [
        make_session(f"s{i}", tags=["a", "b", "c", "d", "e", "f"])
        for i in range(3)
    ]
    stats = compute_tag_stats(sessions)
    assert len(stats.most_common) == 5


def test_mixed_tagged_and_untagged():
    sessions = [
        make_session("s1", tags=["ci"]),
        make_session("s2"),
        make_session("s3", tags=[]),
    ]
    stats = compute_tag_stats(sessions)
    assert stats.sessions_with_tags == 1
    assert stats.sessions_without_tags == 2


def test_format_tag_stats_contains_fields():
    sessions = [make_session("s1", tags=["deploy", "infra"])]
    stats = compute_tag_stats(sessions)
    output = format_tag_stats(stats)
    assert "Total tag usages" in output
    assert "Unique tags" in output
    assert "deploy" in output


def test_format_tag_stats_no_tags_no_top_section():
    stats = compute_tag_stats([])
    output = format_tag_stats(stats)
    assert "Top tags" not in output
