"""Tests for breadcrumb.grapher."""

import pytest
from breadcrumb.session import Session, Step
from breadcrumb.grapher import (
    build_graph,
    format_graph,
    GraphError,
    GraphResult,
    GraphNode,
)


def make_session(commands, notes=None):
    s = Session(name="test-session")
    for i, cmd in enumerate(commands):
        note = (notes or [])[i] if notes and i < len(notes) else ""
        s.steps.append(Step(command=cmd, note=note))
    return s


def test_build_graph_node_count():
    s = make_session(["git init", "git add .", "git commit -m 'init'"])
    result = build_graph(s)
    assert result.node_count == 3


def test_build_graph_sequential_edges():
    s = make_session(["echo a", "echo b", "echo c"])
    result = build_graph(s, link_sequential=True)
    assert result.nodes[0].edges == [1]
    assert result.nodes[1].edges == [2]
    assert result.nodes[2].edges == []


def test_build_graph_no_edges_when_disabled():
    s = make_session(["echo a", "echo b"])
    result = build_graph(s, link_sequential=False)
    for node in result.nodes:
        assert node.edges == []


def test_build_graph_empty_session_raises():
    s = Session(name="empty")
    with pytest.raises(GraphError):
        build_graph(s)


def test_build_graph_preserves_commands():
    cmds = ["ls", "pwd", "whoami"]
    s = make_session(cmds)
    result = build_graph(s)
    assert [n.command for n in result.nodes] == cmds


def test_build_graph_preserves_notes():
    s = make_session(["ls", "pwd"], notes=["list files", "show dir"])
    result = build_graph(s)
    assert result.nodes[0].note == "list files"
    assert result.nodes[1].note == "show dir"


def test_build_graph_session_name():
    s = make_session(["echo hi"])
    s.name = "my-session"
    result = build_graph(s)
    assert result.session_name == "my-session"


def test_edge_count():
    s = make_session(["a", "b", "c", "d"])
    result = build_graph(s)
    assert result.edge_count == 3


def test_format_graph_contains_command():
    s = make_session(["docker build .", "docker run img"])
    result = build_graph(s)
    output = format_graph(result)
    assert "docker build ." in output
    assert "docker run img" in output


def test_format_graph_contains_summary():
    s = make_session(["echo 1", "echo 2"])
    result = build_graph(s)
    output = format_graph(result)
    assert "2 nodes" in output
    assert "1 edges" in output


def test_node_to_dict():
    node = GraphNode(index=0, command="ls", note="list", edges=[1, 2])
    d = node.to_dict()
    assert d["index"] == 0
    assert d["command"] == "ls"
    assert d["note"] == "list"
    assert d["edges"] == [1, 2]
