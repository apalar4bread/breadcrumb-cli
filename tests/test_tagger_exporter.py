"""Tests for breadcrumb.tagger_exporter."""

from __future__ import annotations

import pytest

from breadcrumb.session import Session, add_step
from breadcrumb.tagger import add_tag
from breadcrumb.tagger_exporter import (
    export_tags_to_dict,
    export_tags_flat,
    format_tags_text,
    all_unique_tags,
)


def make_session(name: str = "s") -> Session:
    s = Session(name=name)
    add_step(s, "echo hello")
    return s


def test_export_tags_to_dict_empty_tags():
    s = make_session("alpha")
    result = export_tags_to_dict([s])
    assert result[s.id] == []


def test_export_tags_to_dict_with_tags():
    s = make_session("beta")
    add_tag(s, "ci")
    add_tag(s, "deploy")
    result = export_tags_to_dict([s])
    assert set(result[s.id]) == {"ci", "deploy"}


def test_export_tags_flat_structure():
    s = make_session("gamma")
    add_tag(s, "infra")
    rows = export_tags_flat([s])
    assert len(rows) == 1
    assert rows[0]["session_id"] == s.id
    assert rows[0]["session_name"] == "gamma"
    assert rows[0]["tag"] == "infra"


def test_export_tags_flat_no_tags():
    s = make_session("delta")
    rows = export_tags_flat([s])
    assert rows == []


def test_format_tags_text_no_sessions():
    result = format_tags_text([])
    assert result == "No sessions."


def test_format_tags_text_with_tags():
    s = make_session("epsilon")
    add_tag(s, "staging")
    result = format_tags_text([s])
    assert "epsilon" in result
    assert "staging" in result


def test_format_tags_text_no_tags_shows_none():
    s = make_session("zeta")
    result = format_tags_text([s])
    assert "(none)" in result


def test_all_unique_tags_empty():
    result = all_unique_tags([])
    assert result == []


def test_all_unique_tags_deduplicates():
    s1 = make_session("s1")
    s2 = make_session("s2")
    add_tag(s1, "ci")
    add_tag(s2, "ci")
    add_tag(s2, "deploy")
    result = all_unique_tags([s1, s2])
    assert result == ["ci", "deploy"]


def test_all_unique_tags_sorted():
    s = make_session("s")
    add_tag(s, "zebra")
    add_tag(s, "alpha")
    result = all_unique_tags([s])
    assert result == ["alpha", "zebra"]
