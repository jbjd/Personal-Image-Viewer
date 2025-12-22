"""Validation functions for compilation requirements"""

import tomllib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_module_version
from logging import getLogger
from sys import version_info
from typing import Any

from nuitka import PythonVersions
from personal_compile_tools.converters import version_str_to_tuple, version_tuple_to_str
from personal_compile_tools.requirement_operators import Operators
from personal_compile_tools.requirements import Requirement, parse_requirements_file

from compile_utils.constants import LOGGER_NAME, PROJECT_FILE
from compile_utils.module_dependencies import module_dependencies

_logger = getLogger(LOGGER_NAME)

_required_python_version: tuple[int, int] | None = None


def get_required_python_version() -> tuple[int, int]:
    """Returns tuple representing the required python version
    by parsing it out of the pyproject.toml file."""
    global _required_python_version

    if _required_python_version is not None:
        return _required_python_version

    with open(PROJECT_FILE, "rb") as fp:
        project: dict[str, Any] = tomllib.load(fp)["project"]

    _required_python_version = version_str_to_tuple(
        project["requires-python"][2:]  # type: ignore
    )
    return _required_python_version  # type: ignore


def validate_module_requirements() -> None:
    """Logs warning if installed packages do not match specifications
    in requirements files and raises PackageNotFoundError if they are
    not installed"""
    requirements: list[Requirement] = module_dependencies + parse_requirements_file(
        "requirements_compile.txt"
    )

    missing_modules: list[str] = []

    for requirement in requirements:
        try:
            # personal_compile_tools can't determine direct references,
            # so there is a custom check here
            matches_installed: bool = (
                requirement.matches_installed_version()
                if requirement.rules[0].operator != Operators.DIRECT_REFERENCE
                else _personal_module_matches_installed_version(
                    requirement.name, requirement.rules[0].version.raw_version
                )
            )
            if not matches_installed:
                installed_version: str = get_module_version(requirement.name)
                _logger.warning(
                    "Expected requirement %s but found version %s",
                    requirement,
                    installed_version,
                )
        except PackageNotFoundError:
            missing_modules.append(requirement.name)

    if missing_modules:
        raise PackageNotFoundError(
            f"Missing module dependencies {missing_modules}\n"
            "Please install them to compile"
        )


def validate_python_version() -> None:
    required_python: tuple[int, int] = get_required_python_version()
    used_python: tuple[int, int] = version_info[:2]

    if used_python != required_python:
        _logger.warning(
            "Expecting python version %s but found %s", required_python, used_python
        )

    version: str = version_tuple_to_str(used_python)
    if version in PythonVersions.getNotYetSupportedPythonVersions():
        raise Exception(f"{version} not supported by Nuitka yet")


def validate_PIL() -> None:
    """Ensures installed version of PIL has expected optional modules installed.
    Normal PIL installations will have these, but since PIL can be built from
    source with these turned off, it needs to be checked."""

    missing_modules: list[str] = []

    try:
        from PIL import _avif
    except ImportError:
        missing_modules.append("AVIF")
    else:
        del _avif

    try:
        from PIL import _webp
    except ImportError:
        missing_modules.append("WEBP")
    else:
        del _webp

    if missing_modules:
        raise Exception(
            "Current PIL installation missing necessary modules: "
            + ",".join(missing_modules)
        )


def _personal_module_matches_installed_version(name: str, source_url: str) -> bool:
    """Returns true if the 'personal' modules from the url are the correct version

    Since they are tagged with their version, we can check if the url ends
    with the version"""
    installed_version: str = get_module_version(name)

    return source_url.endswith(f"@v{installed_version}")
