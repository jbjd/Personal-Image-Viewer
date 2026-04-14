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

def parse_config_file() -> Config:
    """Parsed image_viewer/config.ini and returns provided values or default."""
