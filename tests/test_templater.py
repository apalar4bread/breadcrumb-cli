import pytest
from breadcrumb.session import Session
from breadcrumb.templater import (
    Template, create_template, apply_template, template_summary, TemplateError
)


def make_session(name="test"):
    return Session(id="abc", name=name, steps=[], tags=[])


def test_create_template_basic():
    t = create_template("setup", ["git init", "npm install"])
    assert t.name == "setup"
    assert len(t.commands) == 2


def test_create_template_strips_name():
    t = create_template("  setup  ", ["echo hi"])
    assert t.name == "setup"


def test_create_template_blank_name_raises():
    with pytest.raises(TemplateError, match="blank"):
        create_template("  ", ["echo hi"])


def test_create_template_no_commands_raises():
    with pytest.raises(TemplateError, match="at least one"):
        create_template("setup", [])


def test_create_template_with_tags():
    t = create_template("deploy", ["make build"], tags=["ci", "prod"])
    assert "ci" in t.tags
    assert "prod" in t.tags


def test_apply_template_adds_steps():
    t = create_template("setup", ["git init", "npm install"])
    s = make_session()
    s = apply_template(t, s)
    assert len(s.steps) == 2
    assert s.steps[0].command == "git init"
    assert "from template: setup" in s.steps[0].note


def test_apply_template_adds_tags():
    t = create_template("deploy", ["make"], tags=["ci"])
    s = make_session()
    s = apply_template(t, s)
    assert "ci" in s.tags


def test_apply_template_no_duplicate_tags():
    t = create_template("deploy", ["make"], tags=["ci"])
    s = make_session()
    s.tags = ["ci"]
    s = apply_template(t, s)
    assert s.tags.count("ci") == 1


def test_template_roundtrip():
    t = create_template("setup", ["echo hi"], description="A setup template", tags=["dev"])
    d = t.to_dict()
    t2 = Template.from_dict(d)
    assert t2.name == t.name
    assert t2.commands == t.commands
    assert t2.tags == t.tags
    assert t2.description == t.description


def test_template_summary_contains_name():
    t = create_template("build", ["make all", "make test"], description="Build steps")
    summary = template_summary(t)
    assert "build" in summary
    assert "2" in summary
    assert "Build steps" in summary


def test_template_summary_no_tags():
    t = create_template("build", ["make"])
    summary = template_summary(t)
    assert "(none)" in summary
