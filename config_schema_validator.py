"""Validates the config.ini file to ensure it presents accurate examples."""

from abc import abstractmethod
from collections.abc import Callable
from configparser import ConfigParser
from typing import override

from tests.utils._c_bindings import (
    is_empty_or_valid_hex_color,
    is_empty_or_valid_int,
    is_empty_or_valid_keybind,
)


def any_str(_: str) -> bool:
    """Always returns True since any string is valid."""
    return True


schema: dict[str, dict[str, Callable[[str], bool]]] = {
    "CACHE": {"size": is_empty_or_valid_int},
    "KEYBINDS": {
        "copy_to_clipboard_as_base64": is_empty_or_valid_keybind,
        "move_to_new_file": is_empty_or_valid_keybind,
        "optimize_image": is_empty_or_valid_keybind,
        "refresh": is_empty_or_valid_keybind,
        "reload_image": is_empty_or_valid_keybind,
        "rename": is_empty_or_valid_keybind,
        "show_details": is_empty_or_valid_keybind,
        "undo_most_recent_action": is_empty_or_valid_keybind,
    },
    "UI": {"background_color": is_empty_or_valid_hex_color, "font": any_str},
}


config_parser = ConfigParser()
config_parser.read("image_viewer/config.ini")

config: dict[str, dict[str, str]] = {
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
