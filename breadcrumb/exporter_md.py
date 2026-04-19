"""Export sessions to Markdown format."""
from breadcrumb.session import Session


def export_to_markdown(session: Session, verbose: bool = False) -> str:
    """Convert a session to a Markdown document."""
    lines = []
    lines.append(f"# {session.name}")
    lines.append("")
    if session.tags:
        lines.append("**Tags:** " + ", ".join(f"`{t}`" for t in session.tags))
        lines.append("")
    lines.append(f"**Steps:** {len(session.steps)}")
    lines.append("")
    if not session.steps:
        lines.append("_No steps recorded._")
        return "\n".join(lines)

    lines.append("## Steps")
    lines.append("")
    for i, step in enumerate(session.steps, 1):
        note_part = f" — {step.note}" if step.note else ""
        lines.append(f"### Step {i}{note_part}")
        lines.append("")
        lines.append(f"```sh")
        lines.append(step.command)
        lines.append("```")
        if verbose and step.metadata:
            lines.append("")
            lines.append("**Metadata:**")
            for k, v in step.metadata.items():
                lines.append(f"- `{k}`: {v}")
        lines.append("")

    return "\n".join(lines)


def write_markdown(session: Session, path: str, verbose: bool = False) -> None:
    """Write session as Markdown to the given file path."""
    content = export_to_markdown(session, verbose=verbose)
    with open(path, "w") as f:
        f.write(content)
