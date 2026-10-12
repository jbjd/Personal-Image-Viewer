"""Validation functions for compilation requirements"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as get_module_version

from packaging.version import parse as _parse_version
from personal_compile_tools.modules import get_missing_modules
from personal_compile_tools.requirements import Requirement, parse_requirements_file

from compile_utils.log import get_logger
from compile_utils.module_dependencies import module_dependencies

_logger = get_logger()


def validate_module_requirements() -> None:
    """Validates the modules this program depends on are installed and logs warning if
    installed packages do not match version specifications.

    :raises ModuleNotFoundError: If necessary modules are not installed."""

    requirements: list[Requirement] = module_dependencies + parse_requirements_file(
        "requirements_compile.txt"
    )

    missing_modules: list[str] = []

    for requirement in requirements:
        try:
            # personal_compile_tools can't determine direct references,
            # so there is a custom check here
            matches_installed: bool = requirement.matches_installed_version(
                _personal_module_matches_installed_version
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
        raise ModuleNotFoundError(
            f"Missing module dependencies {missing_modules}\n"
            "Please install them to compile"
        )


def validate_PIL() -> None:  # noqa: N802
    """Ensures installed version of PIL has expected optional modules installed.
    Normal PIL installations will have these, but PIL can be built from source with
    these turned off.

    :raises ModuleNotFoundError: If PIL is missing required modules."""

    missing_modules: list[str] = get_missing_modules(
        ["PIL._avif", "PIL._webp", "PIL._imagingft"]
    )

    if missing_modules:
        raise ModuleNotFoundError(
            "Current PIL installation missing necessary modules: "
            + ",".join(missing_modules)
        )


def _personal_module_matches_installed_version(
    installed_version: str, url: str
) -> bool:
    """Checks that the version of 'personal' module's are the correct by their url.
    They are tagged with their version, so the url's end can be used to check.

    :param name: The name of the 'personal' module.
    :param url: Url to the module on github.
    :returns: True if url's tag matches installed version."""

    url_version_index: int = url.rfind("@v")
    if url_version_index == -1:
        raise RuntimeError("Can't parse url: " + url)

    url_version: str = url[url_version_index + 2 :]

    return _parse_version(installed_version) == _parse_version(url_version)
