"""Classes and functions that remove unused code and annotations"""

import os
import subprocess
from collections.abc import Iterator
from glob import glob

from personal_compile_tools.file_operations import (
    read_file_utf8,
    walk_folder,
    write_file_utf8,
)
from personal_python_ast_optimizer.regex.replace import re_replace_file
from personal_simple_tcl_minifier.parse import tcl_minify

from compile_utils.code_to_skip import regex_to_apply_tk
from compile_utils.log import get_logger

SEPARATORS = r"[\\/]" if os.name == "nt" else r"[/]"


_logger = get_logger()


def clean_tk_files(compile_dir: str) -> None:
    """Removes unwanted files that nuitka auto includes in standalone
    and cleans up comments/whitespace from necessary tcl files"""
    for path_or_glob, regexes in regex_to_apply_tk.items():
        glob_result: list[str] = glob(os.path.join(compile_dir, path_or_glob))
        if not glob_result:
            _logger.warning("Glob not found: %s", path_or_glob)
            continue

        # globs are used since files may have versioning in name
        # They are intended to target a single file
        if len(glob_result) > 1:
            _logger.warning("Glob %s found multiple files", path_or_glob)

        code_file: str = glob_result[0]
        re_replace_file(code_file, regexes, raise_if_not_applied=True)

    for code_file in _get_files_in_folder_with_filter(compile_dir, (".tcl", ".tm")):
        source: str = read_file_utf8(code_file)
        source = tcl_minify(source)
        write_file_utf8(code_file, source)


def strip_files(compile_dir: str) -> None:
    """Runs strip on all exe/dll files in provided dir"""

    # TODO: Had issues adding .so here on linux. Should be revisited here at some point
    for strippable_file in _get_files_in_folder_with_filter(
        compile_dir, (".exe", ".dll", ".pyd")
    ):
        result = subprocess.run(["strip", "--strip-all", strippable_file], check=False)  # noqa: S607

        if result.returncode != 0:
            _logger.warning("Failed to strip file %s", strippable_file)


def _get_files_in_folder_with_filter(
    folder_path: str, extension_filter: tuple[str, ...]
) -> Iterator[str]:
    """Gets files in a folder and subfolders that end with certain extensions."""
    return iter(p for p in walk_folder(folder_path) if p.endswith(extension_filter))
