"""CLI commands for session templates."""
import json
import click
from pathlib import Path
from breadcrumb.templater import create_template, apply_template, template_summary, TemplateError, Template
from breadcrumb.store import SessionStore

TEMPLATE_DIR = Path.home() / ".breadcrumb" / "templates"


def _load_template(name: str) -> Template:
    path = TEMPLATE_DIR / f"{name}.json"
    if not path.exists():
        raise click.ClickException(f"Template '{name}' not found.")
    return Template.from_dict(json.loads(path.read_text()))


def _save_template(template: Template) -> None:
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    path = TEMPLATE_DIR / f"{template.name}.json"
    path.write_text(json.dumps(template.to_dict(), indent=2))


@click.group("template")
def template_cmd():
    """Manage and apply session templates."""


@template_cmd.command("create")
@click.argument("name")
@click.option("--cmd", "commands", multiple=True, required=True, help="Commands to include.")
@click.option("--desc", default="", help="Template description.")
@click.option("--tag", "tags", multiple=True, help="Tags to attach.")
def create_cmd(name, commands, desc, tags):
    """Create a new template."""
    try:
        t = create_template(name, list(commands), description=desc, tags=list(tags))
        _save_template(t)
        click.echo(f"Template '{t.name}' created with {len(t.commands)} command(s).")
    except TemplateError as e:
        raise click.ClickException(str(e))


@template_cmd.command("list")
def list_cmd():
    """List available templates."""
    TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    templates = sorted(TEMPLATE_DIR.glob("*.json"))
    if not templates:
        click.echo("No templates found.")
        return
    for p in templates:
        click.echo(p.stem)


@template_cmd.command("info")
@click.argument("name")
def info_cmd(name):
    """Show template details."""
    t = _load_template(name)
    click.echo(template_summary(t))


@template_cmd.command("apply")
@click.argument("name")
@click.argument("session_id")
@click.option("--store-path", default=None, hidden=True)
def apply_cmd(name, session_id, store_path):
    """Apply a template to a session."""
    t = _load_template(name)
    store = SessionStore(store_path) if store_path else SessionStore()
    session = store.load(session_id)
    if session is None:
        raise click.ClickException(f"Session '{session_id}' not found.")
    session = apply_template(t, session)
    store.save(session)
    click.echo(f"Applied template '{name}' to session '{session_id}'. Added {len(t.commands)} step(s).")
