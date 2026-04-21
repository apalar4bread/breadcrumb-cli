import pytest
from breadcrumb.session import Session, Step
from breadcrumb.transposer import (
    TransposeError,
    TransposeResult,
    transpose_steps,
    format_transpose_result,
)


def make_session(commands):
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


def test_transpose_basic():
    s = make_session(["echo a", "echo b", "echo c"])
    result = transpose_steps(s, 0, 2)
    assert s.steps[0].command == "echo c"
    assert s.steps[2].command == "echo a"
    assert s.steps[1].command == "echo b"


def test_transpose_adjacent():
    s = make_session(["first", "second"])
    transpose_steps(s, 0, 1)
    assert s.steps[0].command == "second"
    assert s.steps[1].command == "first"


def test_transpose_result_records_original_commands():
    s = make_session(["alpha", "beta", "gamma"])
    result = transpose_steps(s, 1, 2)
    assert result.command_a == "beta"
    assert result.command_b == "gamma"
    assert result.index_a == 1
    assert result.index_b == 2


def test_transpose_preserves_metadata():
    s = make_session(["cmd1", "cmd2"])
    s.steps[0].metadata["note"] = "important"
    transpose_steps(s, 0, 1)
    assert s.steps[1].metadata["note"] == "important"


def test_transpose_same_index_raises():
    s = make_session(["a", "b"])
    with pytest.raises(TransposeError, match="different"):
        transpose_steps(s, 1, 1)


def test_transpose_out_of_range_raises():
    s = make_session(["a", "b"])
    with pytest.raises(TransposeError, match="out of range"):
        transpose_steps(s, 0, 5)


def test_transpose_negative_index_raises():
    s = make_session(["a", "b"])
    with pytest.raises(TransposeError, match="out of range"):
        transpose_steps(s, -1, 1)


def test_transpose_empty_session_raises():
    s = make_session([])
    with pytest.raises(TransposeError, match="no steps"):
        transpose_steps(s, 0, 1)


def test_format_transpose_result_contains_indices():
    s = make_session(["ls", "pwd"])
    result = transpose_steps(s, 0, 1)
    text = format_transpose_result(result)
    assert "0" in text
    assert "1" in text


def test_format_transpose_result_contains_commands():
    s = make_session(["ls", "pwd"])
    result = transpose_steps(s, 0, 1)
    text = format_transpose_result(result)
    assert "ls" in text
    assert "pwd" in text
