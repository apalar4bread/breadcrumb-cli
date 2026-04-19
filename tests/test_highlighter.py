import pytest
from breadcrumb.highlighter import highlight_command, strip_highlights, _ANSI


def plain(cmd: str) -> str:
    return strip_highlights(highlight_command(cmd, enabled=True))


def test_highlight_disabled_returns_original():
    cmd = "git commit -m 'hello'"
    assert highlight_command(cmd, enabled=False) == cmd


def test_highlight_empty_string():
    assert highlight_command("", enabled=True) == ""


def test_highlight_single_word_command():
    result = highlight_command("ls", enabled=True)
    assert "ls" in result
    assert _ANSI["cmd"] in result


def test_highlight_preserves_text_content():
    cmd = "git commit -m 'hello world'"
    assert plain(cmd) == cmd


def test_highlight_flag_colored():
    result = highlight_command("git --version", enabled=True)
    assert _ANSI["flag"] in result
    assert "--version" in result


def test_highlight_path_colored():
    result = highlight_command("cat /etc/hosts", enabled=True)
    assert _ANSI["path"] in result
    assert "/etc/hosts" in result


def test_highlight_string_colored():
    result = highlight_command("echo 'hello'", enabled=True)
    assert _ANSI["string"] in result


def test_highlight_pipe_colored():
    result = highlight_command("ls | grep foo", enabled=True)
    assert _ANSI["pipe"] in result


def test_highlight_number_colored():
    result = highlight_command("sleep 5", enabled=True)
    assert _ANSI["number"] in result


def test_strip_highlights_removes_ansi():
    result = highlight_command("git --version", enabled=True)
    stripped = strip_highlights(result)
    assert "\033[" not in stripped
    assert "git --version" == stripped


def test_command_word_bold_blue():
    result = highlight_command("docker ps", enabled=True)
    assert result.startswith(_ANSI["cmd"] + "docker")
