"""Validates the config.ini file to ensure it presents accurate examples."""

from abc import abstractmethod
from collections.abc import Callable
from configparser import ConfigParser
from typing import override

from tests.test_util._config import is_valid_hex_color, is_valid_keybind


def _strip_quotes(value: str) -> str:
    """Values from .ini may be wrapped in quotes, return value without quotes"""
    return value.strip("'\"")


def empty_or_valid_hex_color(hex_color: str) -> bool:
    """Returns True if hex_color is in valid format '#abC123'"""
    hex_color = _strip_quotes(hex_color)
    return hex_color == "" or is_valid_hex_color(hex_color)


def empty_or_valid_keybind(keybind: str) -> bool:
    """Returns True if keybind is a valid subset of keybinds used for tkinter
    that this program accepts"""
    keybind = _strip_quotes(keybind)
    return keybind == "" or is_valid_keybind(keybind)


def empty_or_valid_int(possible_int: str) -> bool:
    """Returns True if possible_int is an empty string or parsable as an int"""
    possible_int = _strip_quotes(possible_int)
    try:
        return possible_int == "" or int(possible_int) >= 0
    except ValueError:
        return False


def any_str(_: str) -> bool:
    """Always returns True since any string is valid."""
    return True


schema: dict[str, dict[str, Callable[[str], bool]]] = {
    "CACHE": {"size": empty_or_valid_int},
    "KEYBINDS": {
        "copy_to_clipboard_as_base64": empty_or_valid_keybind,
        "move_to_new_file": empty_or_valid_keybind,
        "optimize_image": empty_or_valid_keybind,
        "refresh": empty_or_valid_keybind,
        "reload_image": empty_or_valid_keybind,
        "rename": empty_or_valid_keybind,
        "show_details": empty_or_valid_keybind,
        "undo_most_recent_action": empty_or_valid_keybind,
    },
    "UI": {"background_color": empty_or_valid_hex_color, "font": any_str},
}


config_parser = ConfigParser()
config_parser.read("image_viewer/config.ini")

config: dict = {
    section: {
        option: config_parser.get(section, option)
        for option in config_parser.options(section)
    }
    for section in config_parser.sections()
}


class SchemaIssue:
    """Represents an issue with the schema"""

    __slots__ = ("key", "section")

    def __init__(self, section: str, key: str) -> None:
        self.section: str = section
        self.key: str = key

    @abstractmethod
    def get_issue_message(self) -> str:
        """Returns user friendly message for an issue with the schema."""


class MissingKey(SchemaIssue):
    __slots__ = ()

    def __init__(self, section: str, key: str) -> None:
        super().__init__(section, key)

    @override
    def get_issue_message(self) -> str:
        return f'Section [{self.section}] key "{self.key}" missing'


class BadKey(SchemaIssue):
    __slots__ = ("bad_value",)

    def __init__(self, section: str, key: str, bad_value: str) -> None:
        super().__init__(section, key)
        self.bad_value: str = bad_value

    @override
    def get_issue_message(self) -> str:
        return f'Section [{self.section}] key "{self.key}" bad value {self.bad_value}'


class UnknownKey(SchemaIssue):
    def __init__(self, section: str, key: str) -> None:
        super().__init__(section, key)

    @override
    def get_issue_message(self) -> str:
        return f'Section [{self.section}] key "{self.key}" is unknown'


issues: list[SchemaIssue] = []


for schema_section, schema_keys in schema.items():
    section: dict[str, str] | None = config.pop(schema_section, None)
    if section is None:
        issues.extend(
            MissingKey(schema_section, schema_key) for schema_key in schema_keys
        )
        continue

    for schema_key, validator in schema_keys.items():
        key: str | None = section.pop(schema_key, None)

        if key is None:
            issues.append(MissingKey(schema_section, schema_key))
            continue

        if not validator(key):
            issues.append(BadKey(schema_section, schema_key, key))

    if section:
        issues.extend(UnknownKey(schema_section, key) for key in section)


if issues:
    for issue in issues:
        print(issue.get_issue_message())

    raise Exception("Issues detected with schema")
