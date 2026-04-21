import pytest

from breadcrumb.session import Session, Step
from breadcrumb.chunker import (
    ChunkError,
    Chunk,
    chunk_session,
    chunk_to_sessions,
    format_chunk_summary,
)


def make_session(commands) -> Session:
    s = Session(name="test")
    for cmd in commands:
        s.steps.append(Step(command=cmd))
    return s


# --- chunk_session ---

def test_chunk_session_even_split():
    s = make_session(["a", "b", "c", "d"])
    chunks = chunk_session(s, 2)
    assert len(chunks) == 2
    assert chunks[0].size == 2
    assert chunks[1].size == 2


def test_chunk_session_uneven_split():
    s = make_session(["a", "b", "c", "d", "e"])
    chunks = chunk_session(s, 2)
    assert len(chunks) == 3
    assert chunks[2].size == 1


def test_chunk_session_size_larger_than_steps():
    s = make_session(["a", "b"])
    chunks = chunk_session(s, 10)
    assert len(chunks) == 1
    assert chunks[0].size == 2


def test_chunk_session_size_one():
    s = make_session(["x", "y", "z"])
    chunks = chunk_session(s, 1)
    assert len(chunks) == 3
    assert all(c.size == 1 for c in chunks)


def test_chunk_session_zero_size_raises():
    s = make_session(["a"])
    with pytest.raises(ChunkError, match=">= 1"):
        chunk_session(s, 0)


def test_chunk_session_empty_raises():
    s = Session(name="empty")
    with pytest.raises(ChunkError, match="no steps"):
        chunk_session(s, 2)


def test_chunk_indices_are_sequential():
    s = make_session(["a", "b", "c", "d", "e", "f"])
    chunks = chunk_session(s, 2)
    assert [c.index for c in chunks] == [0, 1, 2]


# --- chunk_to_sessions ---

def test_chunk_to_sessions_names():
    s = make_session(["a", "b", "c"])
    sessions = chunk_to_sessions(s, 2)
    assert "chunk 1/2" in sessions[0].name
    assert "chunk 2/2" in sessions[1].name


def test_chunk_to_sessions_steps_are_independent():
    s = make_session(["a", "b"])
    sessions = chunk_to_sessions(s, 1)
    sessions[0].steps[0].command = "MODIFIED"
    assert s.steps[0].command == "a"


def test_chunk_to_sessions_preserves_tags():
    s = make_session(["a", "b"])
    s.tags = ["devops", "ci"]
    sessions = chunk_to_sessions(s, 1)
    assert sessions[0].tags == ["devops", "ci"]


# --- format_chunk_summary ---

def test_format_chunk_summary_contains_total():
    s = make_session(["a", "b", "c"])
    chunks = chunk_session(s, 2)
    summary = format_chunk_summary(chunks)
    assert "Total chunks: 2" in summary


def test_format_chunk_summary_lists_each_chunk():
    s = make_session(["a", "b", "c"])
    chunks = chunk_session(s, 1)
    summary = format_chunk_summary(chunks)
    assert "Chunk 1" in summary
    assert "Chunk 2" in summary
    assert "Chunk 3" in summary
