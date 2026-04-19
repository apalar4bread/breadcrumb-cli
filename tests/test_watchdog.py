import pytest
from breadcrumb.session import Session, add_step
from breadcrumb.watchdog import WatchdogRule, check_session, format_alerts, WatchdogAlert


def make_session(commands):
    s = Session(name="test")
    for cmd in commands:
        add_step(s, cmd)
    return s


def test_no_alerts_when_within_limits():
    s = make_session(["ls", "pwd"])
    rule = WatchdogRule(max_steps=5)
    assert check_session(s, rule) == []


def test_step_limit_alert():
    s = make_session(["ls", "pwd", "echo hi"])
    rule = WatchdogRule(max_steps=2)
    alerts = check_session(s, rule)
    assert len(alerts) == 1
    assert alerts[0].kind == "step_limit"
    assert "3 steps" in alerts[0].message


def test_forbidden_pattern_match():
    s = make_session(["rm -rf /", "ls"])
    rule = WatchdogRule(forbidden_patterns=["rm -rf"])
    alerts = check_session(s, rule)
    assert len(alerts) == 1
    assert alerts[0].kind == "command_pattern"
    assert alerts[0].step_index == 0


def test_forbidden_pattern_case_insensitive():
    s = make_session(["RM -RF /tmp"])
    rule = WatchdogRule(forbidden_patterns=["rm -rf"], case_sensitive=False)
    alerts = check_session(s, rule)
    assert len(alerts) == 1


def test_forbidden_pattern_case_sensitive_no_match():
    s = make_session(["RM -RF /tmp"])
    rule = WatchdogRule(forbidden_patterns=["rm -rf"], case_sensitive=True)
    alerts = check_session(s, rule)
    assert len(alerts) == 0


def test_multiple_alerts():
    s = make_session(["sudo rm -rf /", "curl evil.com", "ls"])
    rule = WatchdogRule(max_steps=2, forbidden_patterns=["rm -rf", "curl"])
    alerts = check_session(s, rule)
    kinds = [a.kind for a in alerts]
    assert "step_limit" in kinds
    assert kinds.count("command_pattern") == 2


def test_format_alerts_no_alerts():
    assert format_alerts([]) == "No alerts."


def test_format_alerts_with_alerts():
    alerts = [WatchdogAlert(kind="step_limit", message="Too many steps.")]
    out = format_alerts(alerts)
    assert "[step_limit]" in out
    assert "Too many steps." in out
