import pytest

from image_viewer._config import (
    DEFAULT_CACHE_SIZE,
    DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64,
    DEFAULT_KB_MOVE_TO_NEW_FILE,
    DEFAULT_KB_OPTIMIZE_IMAGE,
    DEFAULT_KB_REFRESH,
    DEFAULT_KB_RELOAD_IMAGE,
    DEFAULT_KB_RENAME,
    DEFAULT_KB_SHOW_DETAILS,
    DEFAULT_KB_UNDO_MOST_RECENT_ACTION,
    DEFAULT_UI_BACKGROUND_COLOR,
    DEFAULT_UI_FONT,
    Config,
    parse_config_file,
)
from tests.test_util._config import is_valid_hex_color, is_valid_keybind


def test_config_reader():
    """Should return all specified values"""
    config: Config = parse_config_file("tests/data/config.ini")

    assert config.cache_size == 100

    assert config.kb_copy_to_clipboard_as_base64 == "<Control-K>"
    assert config.kb_move_to_new_file == "<F6>"
    assert config.kb_optimize_image == "<Control-J>"
    assert config.kb_refresh == "<Control-H>"
    assert config.kb_reload_image == "<F7>"
    assert config.kb_rename == "<F3>"
    assert config.kb_show_details == "<Control-a>"
    assert config.kb_undo_most_recent_action == "<Control-Z>"

    assert config.ui_background_color == "#ABCDEF"
    assert config.ui_font == "test"


def test_config_reader_defaults():
    """Should return all default values"""
    config: Config = parse_config_file("tests/data/config_empty.ini")

    _assert_defaults(config)


def test_config_reader_int_fallback():
    """Should return default when"""
    config: Config = parse_config_file("tests/data/config_bad_values.ini")

    _assert_defaults(config)


@pytest.mark.parametrize(
    ("keybind", "expected"),
    [
        ("asdvbiu34uiyg", False),
        ("<Control-d>", True),
        ("<Control-F12>", True),
        ("<Control->", False),
        ("<F0>", False),
        ("<F1>", True),
        ("<F12>", True),
        ("<F13>", False),
        ("<F91>", False),
        ("<k>", False),
        ("<K>", True),
    ],
)
def test_validate_keybind(keybind: str, expected: bool):
    """Should correctly identify valid keybinds."""
    assert is_valid_keybind(keybind) is expected


@pytest.mark.parametrize(
    ("hex_color", "expected"),
    [
        ("asdvbiu34uiyg", False),
        ("#010101", True),
        ("#01ABEF", True),
        ("#01ABEG", False),
        ("#01", False),
    ],
)
def test_validate_hex(hex_color: str, expected: bool):
    """Should correctly identify valid hexs."""
    assert is_valid_hex_color(hex_color) is expected


def _assert_defaults(config: Config) -> None:
    assert config.cache_size == DEFAULT_CACHE_SIZE

    assert (
        config.kb_copy_to_clipboard_as_base64 == DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64
    )
    assert config.kb_move_to_new_file == DEFAULT_KB_MOVE_TO_NEW_FILE
    assert config.kb_optimize_image == DEFAULT_KB_OPTIMIZE_IMAGE
    assert config.kb_refresh == DEFAULT_KB_REFRESH
    assert config.kb_reload_image == DEFAULT_KB_RELOAD_IMAGE
    assert config.kb_rename == DEFAULT_KB_RENAME
    assert config.kb_show_details == DEFAULT_KB_SHOW_DETAILS
    assert config.kb_undo_most_recent_action == DEFAULT_KB_UNDO_MOST_RECENT_ACTION

    assert config.ui_background_color == DEFAULT_UI_BACKGROUND_COLOR
    assert config.ui_font == DEFAULT_UI_FONT
