from pathlib import Path

from sc_companion.sc_inputmap import (
    find_user_inputmap,
    format_bindings_markdown,
    format_synonym_table,
    parse_inputmap,
)


def test_find_user_inputmap_stub_returns_none():
    assert find_user_inputmap() is None


def test_parse_inputmap_stub_returns_empty(tmp_path: Path):
    assert parse_inputmap(tmp_path / "anything.xml") == {}


def test_format_bindings_markdown_stub_returns_empty():
    assert format_bindings_markdown({"FOO": "m"}) == ""


def test_format_synonym_table_stub_returns_empty():
    assert format_synonym_table({"FOO": "m"}) == ""
