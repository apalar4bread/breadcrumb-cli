"""Builds a simple dependency graph from session steps based on command patterns."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from breadcrumb.session import Session, Step


class GraphError(Exception):
    pass


@dataclass
class GraphNode:
    index: int
    command: str
    note: str
    edges: List[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "command": self.command,
            "note": self.note,
            "edges": list(self.edges),
        }


@dataclass
class GraphResult:
    session_name: str
    nodes: List[GraphNode]

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(n.edges) for n in self.nodes)

    def summary(self) -> str:
        return (
            f"Graph for '{self.session_name}': "
            f"{self.node_count} nodes, {self.edge_count} edges"
        )


def build_graph(session: Session, link_sequential: bool = True) -> GraphResult:
    """Build a graph of steps. Optionally link each step to the next."""
    if not session.steps:
        raise GraphError(f"Session '{session.name}' has no steps to graph.")

    nodes: List[GraphNode] = []
    for i, step in enumerate(session.steps):
        node = GraphNode(
            index=i,
            command=step.command,
            note=step.note or "",
        )
        if link_sequential and i > 0:
            nodes[i - 1].edges.append(i)
        nodes.append(node)

    return GraphResult(session_name=session.name, nodes=nodes)


def format_graph(result: GraphResult) -> str:
    """Return a human-readable representation of the graph."""
    lines = [f"Session: {result.session_name}"]
    for node in result.nodes:
        edge_str = " -> " + ", ".join(str(e) for e in node.edges) if node.edges else ""
        note_str = f"  # {node.note}" if node.note else ""
        lines.append(f"  [{node.index}] {node.command}{note_str}{edge_str}")
    lines.append(result.summary())
    return "\n".join(lines)
