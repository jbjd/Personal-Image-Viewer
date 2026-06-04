"""Utilities to help with calling nuitka."""

import os
import sys
from subprocess import Popen


def start_nuitka_compilation(
    input_file: str, nuitka_args: list[str], working_dir: str, assume_this_machine: bool
) -> Popen:
    """Begins nuitka compilation in a new process.

    :param: input_file: Input file to pass to nuitka
    :param nuitka_args: Nuitka arguments to use
    :working_dir: The working directory for the new process
    :returns: The new process"""

    compile_env: dict[str, str] = _get_nuitka_env(assume_this_machine)
    command: list[str] = get_nuitka_command(input_file, nuitka_args)

    return Popen(command, cwd=working_dir, env=compile_env)


def get_nuitka_command(input_file: str, nuitka_args: list[str]) -> list[str]:
    """Returns the command to compile with nuitka.

    :param python: The name or path of python executable to use
    :param input_file: Input file to pass to nuitka
    :param nuita_args: Nuitka arguments to use"""

    return [
        sys.executable,
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

    # -march=native had a race condition that segfault'ed on startup.
    # Segfaults stop when avx instructions are turned off
    compile_env["CFLAGS"] = (
        "-mno-avx -O3 -fgcse-las -fisolate-erroneous-paths-attribute -fgcse-sm "
        "-ffinite-math-only  -fno-signed-zeros -frename-registers -fsched-pressure"
    )

    if assume_this_machine:
        compile_env["CFLAGS"] += " -march=native -mtune=native"

    return compile_env
