"""Utilities to help with calling nuitka."""

import os
import sys
from importlib.metadata import version as get_module_version
from logging import getLogger
from subprocess import Popen
from sysconfig import get_paths

from personal_compile_tools.file_operations import (
    delete_folder,
    read_file_utf8,
    walk_folder,
    write_file_utf8,
)
from personal_python_ast_optimizer.regex.apply import apply_regex

from compile_utils.code_to_skip import custom_nuitka_regex
from compile_utils.log import LOGGER_NAME

_logger = getLogger(LOGGER_NAME)


def start_nuitka_compilation(
    input_file: str, nuitka_args: list[str], working_dir: str
) -> Popen:
    """Begins nuitka compilation in a new process.

    :param: input_file: Input file to pass to nuitka.
    :param nuitka_args: Nuitka arguments to use.
    :working_dir: The working directory for the new process.
    :returns: The new process."""

    default_python: str = "python" if os.name == "nt" else "bin/python3"
    python_path: str = os.path.join(sys.exec_prefix, default_python)

    _logger.info("Using python install %s for nuitka", python_path)

    compile_env: dict[str, str] = _get_nuitka_env()
    command: list[str] = get_nuitka_command(python_path, input_file, nuitka_args)

    return Popen(command, cwd=working_dir, env=compile_env)


def get_nuitka_command(
    python: str, input_file: str, nuitka_args: list[str]
) -> list[str]:
    """Returns the command to compile with nuitka.

    :param python: The name or path of python to use.
    :param input_file: Input file to pass to nuitka.
    :param nuita_args: Nuitka arguments to use."""

    return [
        python,
        "-X",
        "frozen_modules=off",
        "-OO",
        "-m",
        "nuitka",
        input_file,
        "--must-not-re-execute",
        "--python-flag=-OO,no_annotations,no_warnings,static_hashes",
        "--output-filename=viewer",
    ] + nuitka_args


def _get_nuitka_env() -> dict[str, str]:
    """Modified version of nuitka's reExecuteNuitka function.
    Sets all the same values plus some additional so nuitka does not need to
    redundantly spin itself up again, breaking the custom implementation done here.

    :returns: The environment variables to use when starting nuitka."""

    compile_env = os.environ.copy()

    compile_env["PYTHONHASHSEED"] = "0"

    # -march=native had a race condition that segfault'ed on startup.
    # Segfaults stop when avx instructions are turned off
    compile_env["CFLAGS"] = (
        "-march=native -mtune=native -mno-avx -O3 "
        "-ffinite-math-only -fgcse-las -fgcse-sm -fisolate-erroneous-paths-attribute "
        "-fno-signed-zeros -frename-registers -fsched-pressure"
    )

    # Setup like nuitka would to avoid re-execute
    os.environ["NUITKA_SYS_PREFIX"] = sys.prefix

    from nuitka.importing.PreloadedPackages import (  # type: ignore
        detectPreLoadedPackagePaths,
        detectPthImportedPackages,
    )

    os.environ["NUITKA_NAMESPACES"] = repr(detectPreLoadedPackagePaths())

    site_filename = sys.modules["site"].__file__
    if site_filename is not None:
        if site_filename.endswith(".pyc"):
            site_filename = site_filename[:-4] + ".py"

        os.environ["NUITKA_SITE_FILENAME"] = site_filename

    os.environ["NUITKA_PTH_IMPORTED"] = repr(detectPthImportedPackages())

    user_site = getattr(sys.modules["site"], "USER_SITE", None)
    if user_site is not None:
        os.environ["NUITKA_USER_SITE"] = repr(user_site)

    os.environ["NUITKA_PYTHONPATH"] = repr(sys.path)

    return compile_env


_CUSTOM_NUITKA_VERSION_FILE: str = "version.txt"

# Incremented when edits are made to the custom nuitka to cache break
_CUSTOM_NUITKA_VERSION: int = 0


def setup_custom_nuitka_install(custom_nuitka_path: str) -> None:
    """Copies the current nuitka installation into a local folder
    and applies some regex edits to improve compilation of this program.
    Does nothing if custom folder has been setup previously on this
    version of nuitka/version of this implementation.

    :param custom_nuitka_path: Path to the folder to use."""

    version_file_path: str = os.path.join(
        custom_nuitka_path, _CUSTOM_NUITKA_VERSION_FILE
    )
    expected_version: str = f"{get_module_version('nuitka')}-{_CUSTOM_NUITKA_VERSION}"

    try:
        found_version: str = read_file_utf8(version_file_path).strip()
    except FileNotFoundError:
        pass
    else:
        if found_version == expected_version:
            _logger.info("Custom nuitka setup up-to-date")
            return

    _logger.warning("Setting up custom nuitka implementation...")

    delete_folder(custom_nuitka_path)
    os.makedirs(custom_nuitka_path)

    base_nuitka_path: str = os.path.join(get_paths()["purelib"], "nuitka")

    for path in walk_folder(base_nuitka_path, folders_to_ignore=["__pycache__"]):
        source: str = read_file_utf8(path)

        rel_path: str = path.removeprefix(base_nuitka_path)[1:]
        if os.name == "nt":
            rel_path = rel_path.replace("\\", "/")

        if rel_path in custom_nuitka_regex:
            for regex in custom_nuitka_regex[rel_path]:
                source = apply_regex(source, regex, "custom_nuitka")

        new_path: str = os.path.join(custom_nuitka_path, rel_path)
        write_file_utf8(new_path, source, make_folders=True)

    write_file_utf8(version_file_path, expected_version)

    _logger.warning("Setup complete")
