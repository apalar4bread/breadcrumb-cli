"""Export a session to a self-contained HTML file."""
from __future__ import annotations

from pathlib import Path
from breadcrumb.session import Session

_CSS = """
body{font-family:monospace;background:#1e1e1e;color:#d4d4d4;padding:2rem;}
h1{color:#9cdcfe;}h2{color:#ce9178;}
.step{background:#252526;border-left:4px solid #569cd6;margin:1rem 0;padding:.75rem 1rem;border-radius:4px;}
.cmd{color:#4ec9b0;font-weight:bold;font-size:1.05em;}
.note{color:#ce9178;margin-top:.4rem;}
.meta{color:#808080;font-size:.85em;margin-top:.4rem;}
.tag{background:#264f78;color:#9cdcfe;border-radius:3px;padding:1px 6px;margin-right:4px;font-size:.8em;}
"""


def export_to_html(session: Session) -> str:
    rows = []
    for i, step in enumerate(session.steps, 1):
        tags_html = "".join(
            f'<span class="tag">{t}</span>'
            for t in step.metadata.get("tags", [])
        )
        note_html = f'<div class="note">📝 {step.note}</div>' if step.note else ""
        label = step.metadata.get("label", "")
        label_html = f'<div class="meta">🏷 {label}</div>' if label else ""
        rows.append(
            f'<div class="step">'
            f'<div><strong>#{i}</strong> <span class="cmd">{step.command}</span></div>'
            f'{note_html}'
            f'{label_html}'
            f'<div class="meta">{tags_html}</div>'
            f'<div class="meta">🕒 {step.timestamp}</div>'
            f'</div>'
        )
    steps_html = "\n".join(rows) if rows else "<p>No steps recorded.</p>"
    tag_list = ", ".join(session.tags) if session.tags else "none"
    return (
        f"<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
        f"<title>{session.name}</title><style>{_CSS}</style></head><body>"
        f"<h1>📋 {session.name}</h1>"
        f"<p><strong>ID:</strong> {session.id}</p>"
        f"<p><strong>Tags:</strong> {tag_list}</p>"
        f"<h2>Steps ({len(session.steps)})</h2>"
        f"{steps_html}"
        f"</body></html>"
    )


def write_html(session: Session, path: str) -> Path:
    if not path.endswith(".html"):
        raise ValueError("Output file must have a .html extension")
    out = Path(path)
    out.write_text(export_to_html(session), encoding="utf-8")
    return out
