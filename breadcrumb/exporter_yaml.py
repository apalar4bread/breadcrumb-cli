"""Export sessions to YAML format."""

from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

from breadcrumb.session import Session


class YamlExportError(Exception):
    pass


def export_to_yaml(session: Session, indent: int = 2) -> str:
    """Serialize a session to a YAML string."""
    if yaml is None:
        raise YamlExportError(
            "PyYAML is not installed. Run: pip install pyyaml"
        )

    data = {
        "session": {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at,
            "tags": list(session.tags),
            "metadata": dict(session.metadata),
            "steps": [
                {
                    "index": i + 1,
                    "command": step.command,
                    "note": step.note,
                    "timestamp": step.timestamp,
                    "metadata": dict(step.metadata),
                }
                for i, step in enumerate(session.steps)
            ],
        }
    }

    return yaml.dump(data, default_flow_style=False, indent=indent, sort_keys=False)


def write_yaml(session: Session, path: str) -> Path:
    """Write YAML export to a file. Returns the resolved path."""
    if not path.endswith(".yaml") and not path.endswith(".yml"):
        raise YamlExportError("Output file must have a .yaml or .yml extension.")

    content = export_to_yaml(session)
    out = Path(path)
    out.write_text(content, encoding="utf-8")
    return out
