"""Utilities to help with calling nuitka."""

import os
import sys
from subprocess import Popen

from compile_utils.log import get_logger

_logger = get_logger()


def start_nuitka_compilation(
    input_file: str, nuitka_args: list[str], working_dir: str, assume_this_machine: bool
) -> Popen:
    """Begins nuitka compilation in a new process.

    :param: input_file: Input file to pass to nuitka
    :param nuitka_args: Nuitka arguments to use
    :working_dir: The working directory for the new process
    :returns: The new process"""

    default_python: str = "python" if os.name == "nt" else "bin/python3"
    python_path: str = os.path.join(sys.exec_prefix, default_python)

    _logger.info("Using python install %s for nuitka", python_path)

    compile_env: dict[str, str] = _get_nuitka_env(assume_this_machine)
    command: list[str] = get_nuitka_command(python_path, input_file, nuitka_args)

    return Popen(command, cwd=working_dir, env=compile_env)


def get_nuitka_command(
    python: str, input_file: str, nuitka_args: list[str]
) -> list[str]:
    """Returns the command to compile with nuitka.

    :param python: The name or path of python executable to use
    :param input_file: Input file to pass to nuitka
    :param nuita_args: Nuitka arguments to use"""

    return [
        python,
        "-OO",
        "-m",
        "nuitka",
        input_file,
        "--python-flag=-OO,no_annotations,no_warnings,static_hashes",
        "--output-filename=viewer",
        "--user-plugin=C:/Python/Personal-Image-Viewer/compile_utils/piv_plugin.py",
        *nuitka_args,
    ]


def _get_nuitka_env(assume_this_machine: bool) -> dict[str, str]:
    """Gets the environment variables to be used by nuitka.

    :param assume_this_machine: Turns on machine specific compiler optimizations
    :returns: The environment variables to use when starting nuitka"""

    compile_env = os.environ.copy()

    compile_env["PYTHONHASHSEED"] = "0"  # Ensures nuitka does not re-execute

    # -march=native had a race condition that segfault'ed on startup.
    # Segfaults stop when avx instructions are turned off
    compile_env["CFLAGS"] = (
        "-mno-avx -O3 -fgcse-las -fisolate-erroneous-paths-attribute -fgcse-sm "
        "-ffinite-math-only  -fno-signed-zeros -frename-registers -fsched-pressure"
    )

    if assume_this_machine:
        compile_env["CFLAGS"] += " -march=native -mtune=native"

    return compile_env
