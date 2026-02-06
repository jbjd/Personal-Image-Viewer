"""Setup logic for build folder."""

import os
from functools import lru_cache

from personal_compile_tools.file_operations import read_file_utf8, write_file_utf8

from compile_utils.log import get_logger

_logger = get_logger()


@lru_cache
def _get_version_file_path(folder_path: str, module_name: str) -> str:
    """Gets absolute path to version file for custom modules.

    :param folder_path: Path to custom module
    :param module_name: Name of module
    :returns: Full path to where custom version file should be stored"""

    return os.path.join(folder_path, f"custom_version[{module_name}].txt")


def get_custom_module_version(folder_path: str, module_name: str) -> str | None:
    """Gets version of custom module or None if file can't be read.

    :param folder_path: Path to custom module
    :param module_name: Name of module
    :returns: Version of custom module or None"""

    try:
        return read_file_utf8(_get_version_file_path(folder_path, module_name))
    except OSError:
        return None


@lru_cache
def create_custom_module_version(
    module_version: str, custom_version: int | str, append: str = ""
) -> str:
    """Creates version for custom module.

    :param module_version: Version of original module
    :param custom_version: Version of custom implementation
    :param append: Any arbitrary string to append
    :returns: Created version"""

    return f"{module_version}-{custom_version}\n{append}\n"


def write_custom_module_version(
    folder_path: str,
    module_name: str,
    module_version: str,
    custom_version: int | str,
    append: str = "",
) -> None:
    """Writes version file for custom module.

    :param folder_path: Path to custom module
    :param module_name: Name of module
    :param module_version: Version of original module
    :param custom_version: Version of custom implementation
    :param append: Any arbitrary string to append"""

    contents: str = create_custom_module_version(module_version, custom_version, append)
    file_path: str = _get_version_file_path(folder_path, module_name)

    write_file_utf8(file_path, contents)


def custom_module_version_up_to_date(
    folder_path: str,
    module_name: str,
    module_version: str,
    custom_version: int | str,
    append: str = "",
) -> bool:
    """Checks if custom module is up to date based on provided inputs.

    :param folder_path: Path to custom module
    :param module_name: Name of module
    :param module_version: Version of original module
    :param custom_version: Version of custom implementation
    :param append: Any arbitrary string to append
    :returns: True if up to date"""

    up_to_date: bool = get_custom_module_version(
        folder_path, module_name
    ) == create_custom_module_version(module_version, custom_version, append)

    message: str = (
        "Found cached version of module: %s"
        if up_to_date
        else "Can't find cached version of module: %s"
    )
    _logger.info(message, module_name)

    return up_to_date
