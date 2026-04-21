"""Tests for breadcrumb.digester."""

import pytest

from breadcrumb.digester import (
    DigestResult,
    digest_session,
    digests_match,
    format_digest,
)
from breadcrumb.session import Session, add_step


def make_session(name="test", commands=None):
    s = Session(name=name)
    for cmd in (commands or []):
        add_step(s, cmd)
    return s


def test_digest_empty_session():
    s = make_session("empty")
    result = digest_session(s)
    assert result.is_empty is True
    assert result.step_count == 0
    assert len(result.fingerprint) == 64  # SHA-256 hex


def test_digest_step_count():
    s = make_session(commands=["ls", "pwd", "echo hi"])
    result = digest_session(s)
    assert result.step_count == 3
    assert result.is_empty is False


def test_digest_fingerprint_is_deterministic():
    s1 = make_session(commands=["ls", "pwd"])
    s2 = make_session(commands=["ls", "pwd"])
    r1 = digest_session(s1)
    r2 =    assert r1.fingerprint == r2.fingerprint


def test_digest_fingerprint_order_matters():
    s1 = make_session(commands=["ls", "pwd"])
    s2 = make_session(commands=["pwd", "ls"])
    r1 = digest_session(s1)
    r2 = digest_session(s2)
    assert r1.fingerprint != r2.fingerprint


def test_digest_command_hash_order_independent():
    s1 = make_session(commands=["ls", "pwd"])
    s2 = make_session(commands=["pwd", "ls"])
    r1 = digest_session(s1)
    r2 = digest_session(s2)
    assert r1.command_hash == r2.command_hash


def test_digest_command_hash_case_insensitive():
    s1 = make_session(commands=["LS", "PWD"])
    s2 = make_session(commands=["ls", "pwd"])
    r1 = digest_session(s1)
    r2 = digest_session(s2)
    assert r1.command_hash == r2.command_hash


def test_digests_match_same_commands():
    s1 = make_session(commands=["git status", "git pull"])
    s2 = make_session(commands=["git status", "git pull"])
    assert digests_match(digest_session(s1), digest_session(s2)) is True


def test_digests_match_different_commands():
    s1 = make_session(commands=["ls"])
    s2 = make_session(commands=["pwd"])
    assert digests_match(digest_session(s1), digest_session(s2)) is False


def test_short_fingerprint_length():
    s = make_session(commands=["echo hello"])
    result = digest_session(s)
    assert len(result.short()) == 12


def test_format_digest_contains_name():
    s = make_session(name="my-session", commands=["ls"])
    result = digest_session(s)
    text = format_digest(result)
    assert "my-session" in text
    assert result.fingerprint in text
