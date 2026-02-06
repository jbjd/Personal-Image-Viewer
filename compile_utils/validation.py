"""Validation functions for compilation requirements"""

import tomllib
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_module_version
from sys import version_info
from typing import Any

from nuitka import PythonVersions
from packaging.version import parse as _parse_version
from personal_compile_tools.converters import version_str_to_tuple, version_tuple_to_str
from personal_compile_tools.requirement_operators import Operators
from personal_compile_tools.requirements import Requirement, parse_requirements_file

from compile_utils.constants import PROJECT_FILE
from compile_utils.exceptions import InvalidEnvironmentError
from compile_utils.log import get_logger
from compile_utils.module_dependencies import module_dependencies

_logger = get_logger()

_required_python_version: tuple[int, int] | None = None


def get_required_python_version() -> tuple[int, int]:
    """Returns required python version by parsing it out of the pyproject.toml file.

    :returns: Tuple of the required version."""
    global _required_python_version

    if _required_python_version is not None:
        return _required_python_version

    with open(PROJECT_FILE, "rb") as fp:
        project: dict[str, Any] = tomllib.load(fp)["project"]

    _required_python_version = version_str_to_tuple(project["requires-python"][2:])
    return _required_python_version[:2]


def validate_module_requirements() -> None:
    """Validates the modules this program depends on are installed and logs warning if
    installed packages do not match version specifications.

    :raises InvalidEnvironment: If necessary modules are not installed."""

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
                    requirement.name, requirement.rules[0].version
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
        raise InvalidEnvironmentError(
            f"Missing module dependencies {missing_modules}\n"
            "Please install them to compile"
        )


def validate_python_version() -> None:
    """Validates the current python version is the expected version
    to compile this program and is valid for current nuitka install.

    :raises InvalidEnvironment: If python version isn't what this program expects.
    :raises NotImplementedError: If version isn't supported by this nuitka install."""

    required_python: tuple[int, int] = get_required_python_version()
    used_python: tuple[int, int] = version_info[:2]

    if used_python != required_python:
        raise InvalidEnvironmentError(
            f"Expecting python version {required_python} but found {used_python}"
        )

    version: str = version_tuple_to_str(used_python)
    if version in PythonVersions.getNotYetSupportedPythonVersions():
        raise NotImplementedError(f"{version} not supported by Nuitka yet")


def validate_PIL() -> None:  # noqa: N802
    """Ensures installed version of PIL has expected optional modules installed.
    Normal PIL installations will have these, but PIL can be built from source with
    these turned off.

    :raises InvalidEnvironment: If PIL is missing required modules."""

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

    try:
        from PIL import _imagingft
    except ImportError:
        missing_modules.append("FreeType")
    else:
        del _imagingft

    if missing_modules:
        raise InvalidEnvironmentError(
            "Current PIL installation missing necessary modules: "
            + ",".join(missing_modules)
        )


def _personal_module_matches_installed_version(name: str, url: str) -> bool:
    """Checks that the version of 'personal' module's are the correct by their url.
    They are tagged with their version, so the url's end can be used to check.

    :param name: The name of the 'personal' module.
    :param url: Url to the module on github.
    :returns: True if url's tag matches installed version."""

    installed_version: str = get_module_version(name)

    url_version_index: int = url.rfind("@v")
    if url_version_index == -1:
        raise RuntimeError(f"Can't parse url {url}")

    url_version: str = url[url_version_index + 2 :]

    return _parse_version(installed_version) == _parse_version(url_version)
