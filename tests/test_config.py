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


def test_config_reader():
    """Should return all specified values"""
    config: Config = parse_config_file("tests/data/config.ini")

    assert config.cache_size == 100

    assert config.kb_move_to_new_file == "<F6>"
    assert config.kb_show_details == "<Control-a>"
    assert config.kb_undo_most_recent_action == "<Control-Z>"

    assert config.ui_background_color == "#ABCDEF"
    assert config.ui_font == "test"


def test_config_reader_defaults():
    """Should return all default values"""
    config: Config = parse_config_file("tests/data/config_empty.ini")

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


def test_config_reader_int_fallback():
    """Should return default when"""
    config: Config = parse_config_file("tests/data/config_bad_values.ini")

    assert config.cache_size == DEFAULT_CACHE_SIZE

    assert config.kb_move_to_new_file == DEFAULT_KB_MOVE_TO_NEW_FILE

    assert config.ui_background_color == DEFAULT_UI_BACKGROUND_COLOR
    assert config.ui_font == DEFAULT_UI_FONT


# TODO: Move to CUnit

# @pytest.mark.parametrize(
#     ("keybind", "expected_keybind"),
#     [
#         ("asdvbiu34uiyg", _DEFAULT),
#         ("<Control-d>", "<Control-d>"),
#         ("<Control-F12>", "<Control-F12>"),
#         ("<Control->", _DEFAULT),
#         ("<F0>", _DEFAULT),
#         ("<F1>", "<F1>"),
#         ("<F12>", "<F12>"),
#         ("<F13>", _DEFAULT),
#         ("<F91>", _DEFAULT),
#         ("<k>", _DEFAULT),
#         ("<K>", "<K>"),
#     ],
# )
# def test_validate_keybind_or_default(keybind: str, expected_keybind: str):
#     """Should return original keybind or default if keybind was invalid"""
#     assert _validate_keybind_or_default(keybind, _DEFAULT) == expected_keybind


# @pytest.mark.parametrize(
#     ("hex_color", "expected"),
#     [
#         ("asdvbiu34uiyg", _DEFAULT),
#         ("#010101", "#010101"),
#         ("#01ABEF", "#01ABEF"),
#         ("#01ABEG", _DEFAULT),
#         ("#01", _DEFAULT),
#     ],
# )
# def test_validate_hex_or_default(hex_color: str, expected: str):
#     """Should return original hex or default if it was invalid"""
#     assert _validate_hex_or_default(hex_color, _DEFAULT) == expected
