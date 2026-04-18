import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock
from breadcrumb.cli_validate import validate_cmd
from breadcrumb.session import Session, Step


@pytest.fixture
def runner():
    return CliRunner()


def make_session_with_steps(name="mysession"):
    session = Session(name=name)
    step = Step(command="echo hi")
    session.steps.append(step)
    return session


def invoke(runner, session, session_id="abc123"):
    store = MagicMock()
    store.load.return_value = session
    return runner.invoke(
        validate_cmd,
        [session_id],
        obj={"store": store},
        catch_exceptions=False,
    )


def test_validate_valid_session(runner):
    session = make_session_with_steps()
    result = invoke(runner, session)
    assert result.exit_code == 0
    assert "✓" in result.output


def test_validate_session_not_found(runner):
    store = MagicMock()
    store.load.return_value = None
    result = runner.invoke(
        validate_cmd,
        ["missing"],
        obj={"store": store},
        catch_exceptions=False,
    )
    assert result.exit_code != 0


def test_validate_session_with_empty_step(runner):
    session = Session(name="bad")
    step = Step(command="")
    session.steps.append(step)
    result = invoke(runner, session)
    assert result.exit_code == 2
    assert "✗" in result.output
    assert "ERROR" in result.output


def test_validate_session_no_steps_warns(runner):
    session = Session(name="empty")
    result = invoke(runner, session)
    assert result.exit_code == 0
    assert "WARN" in result.output
