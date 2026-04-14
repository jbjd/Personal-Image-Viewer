from typing import Final

DEFAULT_CACHE_SIZE: Final[int]
DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64: Final[str]
DEFAULT_KB_MOVE_TO_NEW_FILE: Final[str]
DEFAULT_KB_OPTIMIZE_IMAGE: Final[str]
DEFAULT_KB_REFRESH: Final[str]
DEFAULT_KB_RELOAD_IMAGE: Final[str]
DEFAULT_KB_RENAME: Final[str]
DEFAULT_KB_SHOW_DETAILS: Final[str]
DEFAULT_KB_UNDO_MOST_RECENT_ACTION: Final[str]
DEFAULT_UI_BACKGROUND_COLOR: Final[str]
DEFAULT_UI_FONT: Final[str]

class Config:
    """Can't be instantiated in Python.

    Represents config for image viewer."""

    __slots__ = (
        "cache_size",
        "kb_copy_to_clipboard_as_base64",
        "kb_move_to_new_file",
        "kb_optimize_image",
        "kb_refresh",
        "kb_reload_image",
        "kb_rename",
        "kb_show_details",
        "kb_undo_most_recent_action",
        "ui_background_color",
        "ui_font",
    )

def parse_config_file(file_path: str | None = None) -> Config:
    """Parsed image_viewer/config.ini and returns provided values or default.

    :param file_path: Path to config ini file"""
