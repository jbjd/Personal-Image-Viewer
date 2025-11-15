"""Functions to help with calling nuitka"""

import os
from logging import getLogger
from subprocess import Popen

from personal_compile_tools.file_operations import copy_folder, delete_folder
from personal_python_ast_optimizer.regex.apply import apply_regex_to_file

from compile_utils.code_to_skip import custom_nuitka_regex
from compile_utils.constants import LOGGER_NAME

_logger = getLogger(LOGGER_NAME)


def start_nuitka_compilation(
    python_path: str,
    nuitka_install: str,
    input_file: str,
    nuitka_args: list[str],
    working_dir: str,
) -> Popen:
    """Begins nuitka compilation in another process"""

    _logger.info("Using python install %s for nuitka", python_path)

    compile_env = get_nuitka_env()
    command: list[str] = get_nuitka_command(
        python_path, nuitka_install, input_file, nuitka_args
    )

    return Popen(command, cwd=working_dir, env=compile_env)


def get_nuitka_command(
    python_path: str, nuitka_install: str, input_file: str, nuitka_args: list[str]
) -> list[str]:
    """Returns the command that this package uses to compile"""
    command: list[str] = [
        python_path,
        "-X",
        "frozen_modules=off",
        "-OO",
        "-m",
        nuitka_install,
        input_file,
        "--must-not-re-execute",
        "--python-flag=-OO,no_annotations,no_warnings,static_hashes",
        "--output-filename=viewer",
    ] + nuitka_args

    return command


def get_nuitka_env() -> dict[str, str]:
    compile_env = os.environ.copy()

    compile_env["PYTHONHASHSEED"] = "0"

    # -march=native had a race condition that segfault'ed on startup.
    # Segfaults stop when avx instructions are turned off
    compile_env["CFLAGS"] = (
        "-march=native -mtune=native -mno-avx -O3 "
        "-ffinite-math-only -fgcse-las -fgcse-sm -fisolate-erroneous-paths-attribute "
        "-fno-signed-zeros -frename-registers -fsched-pressure"
    )

    return compile_env


_CUSTOM_NUITKA_VERSION_FILE: str = "version.txt"

# Incremented when edits are made to the custom nuitka to cache break
_CUSTOM_NUITKA_VERSION: int = 0


def setup_custom_nuitka_install(base_nuitka_path: str, custom_nuitka_path: str):
    pass
    # version_file_path: str = os.path.join(
    #     custom_nuitka_path, _CUSTOM_NUITKA_VERSION_FILE
    # )

    # try:
    #     with open(version_file_path, "r", encoding="utf-8") as fp:
    #         found_version: int = int(fp.read().strip())
    # except FileNotFoundError:
    #     pass
    # else:
    #     if found_version == _CUSTOM_NUITKA_VERSION:
    #         return  # Up to date

    # delete_folder(custom_nuitka_path)
    # copy_folder(base_nuitka_path, custom_nuitka_path)

    # for relative_path, regex in custom_nuitka_regex:
    #     path: str = os.path.join(custom_nuitka_path, relative_path)
    #     apply_regex_to_file(path, regex, "custom_nuitka")
