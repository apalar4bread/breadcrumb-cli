"""Tests for breadcrumb.tagger_importer."""

import pytest

from breadcrumb.session import Session
from breadcrumb.tagger_importer import (
    TagImportError,
    TagImportResult,
    import_tags_from_dict,
    import_tags_from_list,
    import_tags_from_text,
)


def make_session(name="my-session", tags=None):
    s = Session(name=name)
    s.id = "test-id"
    if tags:
        s.tags = list(tags)
    return s


def test_import_from_list_adds_tags():
    s = make_session()
    result = import_tags_from_list(s, ["alpha", "beta"])
    assert "alpha" in s.tags
    assert "beta" in s.tags
    assert result.added_count == 2
    assert result.skipped_count == 0


def test_import_from_list_skips_duplicates():
    s = make_session(tags=["alpha"])
    result = import_tags_from_list(s, ["alpha", "beta"])
    assert result.added_count == 1
    assert result.skipped_count == 1
    assert result.tags_skipped == ["alpha"]


def test_import_from_list_normalizes_case():
    s = make_session()
    import_tags_from_list(s, ["UPPER", "MixedCase"])
    assert "upper" in s.tags
    assert "mixedcase" in s.tags


def test_import_from_list_skips_empty_strings():
    s = make_session()
    result = import_tags_from_list(s, ["", "  ", "valid"])
    assert result.added_count == 1
    assert result.skipped_count == 2


def test_import_from_dict_uses_session_name():
    s = make_session(name="proj-a")
    data = {"proj-a": ["tag1"], "proj-b": ["tag2"]}
    result = import_tags_from_dict(s, data)
    assert "tag1" in s.tags
    assert "tag2" not in s.tags
    assert result.added_count == 1


def test_import_from_dict_missing_key_adds_nothing():
    s = make_session(name="proj-a")
    data = {"other": ["tag1"]}
    result = import_tags_from_dict(s, data)
    assert result.added_count == 0


def test_import_from_text_comma_separated():
    s = make_session()
    result = import_tags_from_text(s, "foo, bar, baz")
    assert result.added_count == 3
    assert "foo" in s.tags


def test_import_from_text_newline_separated():
    s = make_session()
    result = import_tags_from_text(s, "foo\nbar\nbaz")
    assert result.added_count == 3


def test_import_raises_if_no_session_id():
    s = Session(name="no-id")
    with pytest.raises(TagImportError):
        import_tags_from_list(s, ["tag"])


def test_summary_message_format():
    s = make_session(tags=["existing"])
    result = import_tags_from_list(s, ["existing", "new"])
    summary = result.summary()
    assert "1 tag(s) added" in summary
    assert "1 skipped" in summary
    assert s.name in summary
