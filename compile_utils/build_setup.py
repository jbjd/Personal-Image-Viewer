"""Setup logic for build folder."""

import os
from functools import lru_cache

from personal_compile_tools.file_operations import read_file_utf8, write_file_utf8

_CUSTOM_VERSION_FILE: str = "custom_version.txt"


def get_custom_module_version(path: str) -> str | None:
    try:
        return read_file_utf8(os.path.join(path, _CUSTOM_VERSION_FILE))
    except OSError:
        return None


@lru_cache
def create_custom_module_version(
    module_version: str, custom_version: int | str, append: str = ""
) -> str:
    return f"{module_version}-{custom_version}\n{append}\n"


def write_custom_module_version(
    path: str, module_version: str, custom_version: int | str, append: str = ""
) -> None:
    contents: str = create_custom_module_version(module_version, custom_version, append)
    write_file_utf8(os.path.join(path, _CUSTOM_VERSION_FILE), contents)


def custom_module_version_up_to_date(
    path: str, module_version: str, custom_version: int | str, append: str = ""
) -> bool:
    return get_custom_module_version(path) == create_custom_module_version(
        module_version, custom_version, append
    )
