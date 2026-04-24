"""Tests for breadcrumb.aliaser."""

import pytest

from breadcrumb.session import Session
from breadcrumb.aliaser import (
    AliasError,
    set_alias,
    clear_alias,
    get_alias,
    find_by_alias,
    list_aliases,
)


def make_session(name: str = "demo") -> Session:
    return Session(name=name)


# --- set_alias ---

def test_set_alias_valid():
    s = make_session()
    result = set_alias(s, "my-alias")
    assert result == "my-alias"
    assert s.metadata["alias"] == "my-alias"


def test_set_alias_normalizes_case():
    s = make_session()
    set_alias(s, "MyAlias")
    assert get_alias(s) == "myalias"


def test_set_alias_strips_whitespace():
    s = make_session()
    set_alias(s, "  deploy  ")
    assert get_alias(s) == "deploy"


def test_set_alias_empty_raises():
    s = make_session()
    with pytest.raises(AliasError, match="empty"):
        set_alias(s, "")


def test_set_alias_too_long_raises():
    s = make_session()
    with pytest.raises(AliasError, match="32 characters"):
        set_alias(s, "a" * 33)


def test_set_alias_invalid_chars_raises():
    s = make_session()
    with pytest.raises(AliasError, match="invalid characters"):
        set_alias(s, "hello world!")


def test_set_alias_allows_digits_hyphens_underscores():
    s = make_session()
    set_alias(s, "step_1-ok")
    assert get_alias(s) == "step_1-ok"


# --- clear_alias ---

def test_clear_alias_removes_metadata():
    s = make_session()
    set_alias(s, "temp")
    clear_alias(s)
    assert get_alias(s) is None


def test_clear_alias_no_error_if_not_set():
    s = make_session()
    clear_alias(s)  # should not raise


# --- find_by_alias ---

def test_find_by_alias_returns_matching_session():
    s1 = make_session("alpha")
    s2 = make_session("beta")
    set_alias(s1, "a")
    set_alias(s2, "b")
    assert find_by_alias([s1, s2], "b") is s2


def test_find_by_alias_case_insensitive():
    s = make_session()
    set_alias(s, "prod")
    assert find_by_alias([s], "PROD") is s


def test_find_by_alias_returns_none_when_missing():
    s = make_session()
    assert find_by_alias([s], "nope") is None


# --- list_aliases ---

def test_list_aliases_returns_mapping():
    s1 = make_session("session-one")
    s2 = make_session("session-two")
    set_alias(s1, "one")
    set_alias(s2, "two")
    result = list_aliases([s1, s2])
    assert result == {"one": "session-one", "two": "session-two"}


def test_list_aliases_skips_unaliased():
    s1 = make_session("with-alias")
    s2 = make_session("no-alias")
    set_alias(s1, "wa")
    result = list_aliases([s1, s2])
    assert "wa" in result
    assert len(result) == 1


def test_list_aliases_empty_sessions():
    assert list_aliases([]) == {}
