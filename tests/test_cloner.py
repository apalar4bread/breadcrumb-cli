import pytest
from breadcrumb.session import Session, Step
from breadcrumb.cloner import clone_session, clone_steps_only, CloneError


def make_session(name="demo", num_steps=2):
    steps = [
        Step(command=f"echo {i}", note=f"note {i}", metadata={"x": str(i)})
        for i in range(num_steps)
    ]
    return Session(id="abc", name=name, created_at="2024-01-01T00:00:00", steps=steps, tags=["t1"])


def test_clone_has_new_id():
    s = make_session()
    c = clone_session(s)
    assert c.id != s.id


def test_clone_default_name():
    s = make_session(name="my-session")
    c = clone_session(s)
    assert c.name == "my-session (copy)"


def test_clone_custom_name():
    s = make_session()
    c = clone_session(s, new_name="new-name")
    assert c.name == "new-name"


def test_clone_steps_are_independent():
    s = make_session()
    c = clone_session(s)
    c.steps[0].command = "changed"
    assert s.steps[0].command != "changed"


def test_clone_tags_are_independent():
    s = make_session()
    c = clone_session(s)
    c.tags.append("extra")
    assert "extra" not in s.tags


def test_clone_metadata_is_independent():
    s = make_session()
    c = clone_session(s)
    c.steps[0].metadata["new"] = "val"
    assert "new" not in s.steps[0].metadata


def test_clone_blank_name_raises():
    s = make_session()
    with pytest.raises(CloneError):
        clone_session(s, new_name="   ")


def test_clone_name_too_long_raises():
    s = make_session()
    with pytest.raises(CloneError):
        clone_session(s, new_name="x" * 121)


def test_clone_empty_session():
    s = make_session(num_steps=0)
    c = clone_session(s)
    assert c.steps == []


def test_clone_steps_only_basic():
    s = make_session(num_steps=3)
    steps = clone_steps_only(s, [0, 2])
    assert len(steps) == 2
    assert steps[0].command == s.steps[0].command
    assert steps[1].command == s.steps[2].command


def test_clone_steps_only_out_of_range():
    s = make_session(num_steps=2)
    with pytest.raises(CloneError):
        clone_steps_only(s, [5])
