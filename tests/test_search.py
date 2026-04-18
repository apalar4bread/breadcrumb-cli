import pytest
from breadcrumb.session import Session, Step
from breadcrumb.search import (
    search_steps_by_command,
    search_steps_by_note,
    search_sessions_by_name,
)


@pytest.fixture
def sessions():
    s1 = Session(name="deploy-prod")
    s1.add_step("git push origin main")
    s1.add_step("kubectl apply -f deployment.yaml", metadata={"note": "apply k8s config"})

    s2 = Session(name="local-setup")
    s2.add_step("pip install -r requirements.txt", metadata={"note": "install deps"})
    s2.add_step("python manage.py migrate")

    return [s1, s2]


def test_search_steps_by_command_found(sessions):
    results = search_steps_by_command(sessions, "kubectl")
    assert len(results) == 1
    session, step = results[0]
    assert session.name == "deploy-prod"
    assert "kubectl" in step.command


def test_search_steps_by_command_case_insensitive(sessions):
    results = search_steps_by_command(sessions, "GIT")
    assert len(results) == 1
    assert "git" in results[0][1].command


def test_search_steps_by_command_case_sensitive_no_match(sessions):
    results = search_steps_by_command(sessions, "GIT", case_sensitive=True)
    assert results == []


def test_search_steps_by_command_not_found(sessions):
    results = search_steps_by_command(sessions, "docker")
    assert results == []


def test_search_steps_by_note_found(sessions):
    results = search_steps_by_note(sessions, "deps")
    assert len(results) == 1
    _, step = results[0]
    assert step.metadata["note"] == "install deps"


def test_search_steps_by_note_no_note_field(sessions):
    # steps without a note should not raise
    results = search_steps_by_note(sessions, "git")
    assert results == []


def test_search_sessions_by_name(sessions):
    results = search_sessions_by_name(sessions, "deploy")
    assert len(results) == 1
    assert results[0].name == "deploy-prod"


def test_search_sessions_by_name_no_match(sessions):
    results = search_sessions_by_name(sessions, "staging")
    assert results == []


def test_search_sessions_by_name_case_insensitive(sessions):
    results = search_sessions_by_name(sessions, "LOCAL")
    assert len(results) == 1
    assert results[0].name == "local-setup"
