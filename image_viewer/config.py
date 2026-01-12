"""Config values and tools to read them."""

import os
from configparser import ConfigParser
from enum import StrEnum

from image_viewer.util._generic import is_valid_hex_color, is_valid_keybind

DEFAULT_FONT: str = "arial.ttf" if os.name == "nt" else "LiberationSans-Regular.ttf"
DEFAULT_MAX_ITEMS_IN_CACHE: int = 20
DEFAULT_BACKGROUND_COLOR: str = "#000000"


def _validate_hex_or_default(hex_color: str, default: str) -> str:
    """Returns hex_color if its in the valid hex format or default if not

    :param hex_color: A possible hex color
    :param default: What to return if hex_color is invalid
    :returns: Either hex_color if its valid or default"""

    return hex_color if is_valid_hex_color(hex_color) else default


def _validate_keybind_or_default(keybind: str, default: str) -> str:
    """Returns keybind if its in a valid format or default if not

    :param keybind: A possible keybind
    :param default: What to return if keybind is invalid
    :returns: Either keybind if its valid or default"""

    return keybind if is_valid_keybind(keybind) else default


class DefaultKeybinds(StrEnum):
    """Defaults for keybinds that config.ini can override."""

    COPY_TO_CLIPBOARD_AS_BASE64 = "<Control-E>"
    MOVE_TO_NEW_FILE = "<Control-m>"
    OPTIMIZE_IMAGE = "<Control-o>"
    REFRESH = "<Control-r>"
    RELOAD_IMAGE = "<F5>"
    RENAME = "<F2>"
    SHOW_DETAILS = "<Control-d>"
    UNDO_MOST_RECENT_ACTION = "<Control-z>"


class Config:
    """Reads values from config.ini file."""

    __slots__ = ("background_color", "font_file", "keybinds", "max_items_in_cache")

    def __init__(
        self, working_directory: str, config_file_name: str = "config.ini"
    ) -> None:
        config_parser: ConfigParserExt = ConfigParserExt()
        config_parser.read(os.path.join(working_directory, config_file_name))

        self.font_file: str = config_parser.get_string_safe(
            "FONT", "DEFAULT", DEFAULT_FONT
        )
        self.max_items_in_cache: int = config_parser.get_int_safe(
            "CACHE", "SIZE", DEFAULT_MAX_ITEMS_IN_CACHE
        )

        self.keybinds = KeybindConfig(
            config_parser.get_string_safe("KEYBINDS", "COPY_TO_CLIPBOARD_AS_BASE64"),
            config_parser.get_string_safe("KEYBINDS", "MOVE_TO_NEW_FILE"),
            config_parser.get_string_safe("KEYBINDS", "OPTIMIZE_IMAGE"),
            config_parser.get_string_safe("KEYBINDS", "REFRESH"),
            config_parser.get_string_safe("KEYBINDS", "RELOAD_IMAGE"),
            config_parser.get_string_safe("KEYBINDS", "RENAME"),
            config_parser.get_string_safe("KEYBINDS", "SHOW_DETAILS"),
            config_parser.get_string_safe("KEYBINDS", "UNDO_MOST_RECENT_ACTION"),
        )

        self.background_color = _validate_hex_or_default(
            config_parser.get_string_safe(
                "UI", "BACKGROUND_COLOR", DEFAULT_BACKGROUND_COLOR
            ),
            DEFAULT_BACKGROUND_COLOR,
        )


class KeybindConfig:
    """Contains configurable tkinter keybinds."""

    __slots__ = (
        "copy_to_clipboard_as_base64",
        "move_to_new_file",
        "optimize_image",
        "refresh",
        "reload_image",
        "rename",
        "show_details",
        "undo_most_recent_action",
    )

    def __init__(
        self,
        copy_to_clipboard_as_base64: str,
        move_to_new_file: str,
        optimize_image: str,
        refresh: str,
        reload_image: str,
        rename: str,
        show_details: str,
        undo_most_recent_action: str,
    ) -> None:
        self.copy_to_clipboard_as_base64: str = _validate_keybind_or_default(
            copy_to_clipboard_as_base64, DefaultKeybinds.COPY_TO_CLIPBOARD_AS_BASE64
        )
        self.move_to_new_file: str = _validate_keybind_or_default(
            move_to_new_file, DefaultKeybinds.MOVE_TO_NEW_FILE
        )
        self.optimize_image = _validate_keybind_or_default(
            optimize_image, DefaultKeybinds.OPTIMIZE_IMAGE
        )
        self.refresh: str = _validate_keybind_or_default(
            refresh, DefaultKeybinds.REFRESH
        )
        self.reload_image: str = _validate_keybind_or_default(
            reload_image, DefaultKeybinds.RELOAD_IMAGE
        )
        self.rename: str = _validate_keybind_or_default(rename, DefaultKeybinds.RENAME)
        self.show_details: str = _validate_keybind_or_default(
            show_details, DefaultKeybinds.SHOW_DETAILS
        )
        self.undo_most_recent_action: str = _validate_keybind_or_default(
            undo_most_recent_action, DefaultKeybinds.UNDO_MOST_RECENT_ACTION
        )


class ConfigParserExt(ConfigParser):
    """Extends ConfigParser to add safer implementations of get."""

    def get_int_safe(self, section: str, option: str, fallback: int) -> int:
        """Returns config option converted to int or default if convert fails."""
        try:
            result: int = int(super().get(section, option, fallback=fallback))
        except ValueError:
            result = fallback

        return result

    def get_string_safe(self, section: str, option: str, fallback: str = "") -> str:
        """Returns config option as string or default if missing or empty."""
        result: str = super().get(section, option, fallback=fallback).strip("'\"")

        return result or fallback
