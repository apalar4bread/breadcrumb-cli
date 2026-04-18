import pytest
from breadcrumb.colorizer import (
    colorize,
    color_command,
    color_note,
    color_tag,
    color_label,
    color_index,
    color_error,
    color_success,
    color_session_name,
    ANSI,
)


def test_colorize_enabled_wraps_text():
    result = colorize("hello", "green")
    assert "hello" in result
    assert ANSI["green"] in result
    assert ANSI["reset"] in result


def test_colorize_disabled_returns_plain():
    result = colorize("hello", "green", enabled=False)
    assert result == "hello"


def test_colorize_unknown_style_ignored():
    result = colorize("hi", "nonexistent", enabled=True)
    assert "hi" in result


def test_colorize_multiple_styles():
    result = colorize("bold green", "green", "bold")
    assert ANSI["green"] in result
    assert ANSI["bold"] in result


def test_color_command_contains_text():
    assert "ls -la" in color_command("ls -la")


def test_color_command_disabled():
    assert color_command("ls", enabled=False) == "ls"


def test_color_note_contains_text():
    assert "my note" in color_note("my note")


def test_color_tag_prefixes_hash():
    result = color_tag("deploy", enabled=False)
    assert result == "#deploy"


def test_color_label_wraps_brackets():
    result = color_label("urgent", enabled=False)
    assert result == "[urgent]"


def test_color_index_stringifies():
    result = color_index(3, enabled=False)
    assert result == "3"


def test_color_error_disabled():
    assert color_error("oops", enabled=False) == "oops"


def test_color_success_disabled():
    assert color_success("ok", enabled=False) == "ok"


def test_color_session_name_disabled():
    assert color_session_name("my-session", enabled=False) == "my-session"
