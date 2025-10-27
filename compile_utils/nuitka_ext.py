"""Functions to help with calling nuitka"""

import os
from logging import getLogger
from subprocess import Popen

from compile_utils.constants import LOGGER_NAME

_logger = getLogger(LOGGER_NAME)


def start_nuitka_compilation(
    python_path: str, input_file: str, working_dir: str, nuitka_args: list[str]
) -> Popen:
    """Begins nuitka compilation in another process"""

    _logger.info("Using python install %s for nuitka", python_path)

    compile_env = os.environ.copy()
    # -march=native had a race condition that segfault'ed on startup
    # -mtune=native works as intended
    compile_env["CFLAGS"] = "-O3 -fno-signed-zeros -mtune=native"

    command: list[str] = get_nuitka_command(python_path, input_file, nuitka_args)

    return Popen(command, cwd=working_dir, env=compile_env)


def get_nuitka_command(
    python_path: str, input_file: str, nuitka_args: list[str]
) -> list[str]:
    """Returns the command that this package uses to compile"""
    command: list[str] = [
        python_path,
        "-OO",
        "-m",
        "nuitka",
        input_file,
        "--python-flag=-OO,no_annotations,no_warnings,static_hashes",
        "--output-filename=viewer",
    ] + nuitka_args

    return command
