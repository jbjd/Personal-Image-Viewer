"""Utilities to help with calling nuitka."""

import os
import sys
import xml.etree.ElementTree as ET
from collections.abc import Callable
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

    compile_env: dict[str, str] = _get_nuitka_env(assume_this_machine)
    command: list[str] = get_nuitka_command(input_file, nuitka_args)

    return Popen(command, cwd=working_dir, env=compile_env)


def get_nuitka_command(input_file: str, nuitka_args: list[str]) -> list[str]:
    """Returns the command to compile with nuitka.

    :param python: The name or path of python executable to use
    :param input_file: Input file to pass to nuitka
    :param nuita_args: Nuitka arguments to use"""

    plugin_path: str = os.path.join(os.path.dirname(__file__), "piv_plugin.py")

    return [
        sys.executable,
        "-OO",
        "-m",
        "nuitka",
        input_file,
        "--python-flag=-OO,no_annotations,no_warnings,static_hashes",
        "--output-filename=viewer",
        "--user-plugin=" + plugin_path,
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


def clean_compilation_report(report_path: str, warn_on_failure: bool) -> None:
    """The internal PivPlugin for nuitka truncates std modules and removed some dlls.
    They are still included in the report which can make it harder to determine future
    updates to the plugin. This removes those modules/dlls.

    :param report_path: Path to the report file
    :param warn_on_failure: Warns on failure such as no data on what was removed"""

    tree: ET.ElementTree[ET.Element[str]] = ET.parse(report_path)  # noqa: S314
    root: ET.Element | None = tree.getroot()

    if root is None:
        return _warn_cannot_clean_report("Can't find root", warn_on_failure)

    piv_node: ET.Element | None = root.find("./plugins/plugin[@name='PivPlugin']")

    if piv_node is None:
        return _warn_cannot_clean_report("Can't find PivPlugin node", warn_on_failure)

    try:
        removed_std_modules: list[str] = piv_node.attrib["removed_std_modules"].split(
            ","
        )
        removed_std_extensions: list[str] = piv_node.attrib[
            "removed_std_extensions"
        ].split(",")
        removed_dlls: list[str] = piv_node.attrib["removed_dlls"].split(",")

        # Extensions are modules so need to combine
        removed_std_modules += [
            ".".join(m.split(".")[:-1]) for m in removed_std_extensions
        ]

        def __std_module_name_or_package_removed(module_name: str | None) -> bool:
            nonlocal removed_std_modules
            return module_name is not None and (
                module_name in removed_std_modules
                or module_name.split(".")[0] in removed_std_modules
            )

        def __cleaning_pass(
            root: ET.Element,
            condition: str,
            remove_if: Callable[[str | None], bool],
        ) -> None:
            for e in root.findall(condition):
                if remove_if(e.attrib.get("name")):
                    root.remove(e)

        if removed_std_modules:
            __cleaning_pass(root, "./module", __std_module_name_or_package_removed)
            main_usage_root: ET.Element | None = root.find(
                "./module[@name='__main__']/module_usages"
            )
            if main_usage_root is not None:
                __cleaning_pass(
                    main_usage_root,
                    "module_usage",
                    __std_module_name_or_package_removed,
                )

        if removed_std_extensions:
            __cleaning_pass(
                root,
                "./included_extension",
                lambda name: name in removed_std_extensions,
            )

        if removed_dlls:
            __cleaning_pass(root, "./included_dll", lambda name: name in removed_dlls)

        with open(report_path, "wb") as fp:
            tree.write(fp)
    except Exception as e:  # noqa: BLE001
        _warn_cannot_clean_report(str(e), warn_on_failure)


def _warn_cannot_clean_report(message: str, warn_on_failure: bool) -> None:
    if warn_on_failure:
        _logger.warning("Can't clean compilation report: %s", message)
