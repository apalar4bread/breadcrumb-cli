"""Tests for breadcrumb.streaker."""
import pytest
from datetime import datetime, timezone, timedelta
from breadcrumb.session import Session, Step
from breadcrumb.streaker import compute_streak, format_streak, StreakResult


def make_session(commands_with_days):
    """commands_with_days: list of (cmd, days_ago int)."""
    s = Session(id="s1", name="test")
    for cmd, days_ago in commands_with_days:
        day = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT12:00:00")
        s.steps.append(Step(command=cmd, timestamp=day))
    return s


def test_empty_sessions_returns_zero_streak():
    result = compute_streak([])
    assert result.current_streak == 0
    assert result.longest_streak == 0
    assert result.active_days == []


def test_single_day_today():
    s = make_session([("ls", 0)])
    result = compute_streak([s])
    assert result.current_streak == 1
    assert result.longest_streak == 1
    assert len(result.active_days) == 1


def test_consecutive_days_streak():
    s = make_session([("ls", 0), ("pwd", 1), ("echo", 2)])
    result = compute_streak([s])
    assert result.current_streak == 3
    assert result.longest_streak == 3


def test_broken_streak_resets_current():
    # active 0, 1 days ago but gap at 3 days ago
    s = make_session([("ls", 0), ("pwd", 1), ("echo", 4)])
    result = compute_streak([s])
    assert result.current_streak == 2
    assert result.longest_streak == 2


def test_longest_streak_in_past():
    # 5,6,7 days ago = 3 consecutive; 0,1 = 2 consecutive
    s = make_session([("a", 5), ("b", 6), ("c", 7), ("d", 0), ("e", 1)])
    result = compute_streak([s])
    assert result.longest_streak == 3
    assert result.current_streak == 2


def test_multiple_steps_same_day_count_once():
    s = make_session([("ls", 0), ("pwd", 0), ("echo", 0)])
    result = compute_streak([s])
    assert result.current_streak == 1
    assert len(result.active_days) == 1


def test_format_streak_contains_keys():
    r = StreakResult(current_streak=3, longest_streak=5, active_days=["2024-01-01"], last_active="2024-01-01")
    out = format_streak(r)
    assert "3" in out
    assert "5" in out
    assert "2024-01-01" in out


def test_last_active_set_correctly():
    s = make_session([("ls", 2), ("pwd", 5)])
    result = compute_streak([s])
    assert result.last_active != ""
