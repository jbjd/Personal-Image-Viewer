"""Classes and functions that remove unused code and annotations"""

import os
import re
import subprocess
from collections.abc import Iterator
from glob import glob
from logging import getLogger
from re import sub

from personal_compile_tools.file_operations import (
    copy_file,
    read_file_utf8,
    walk_folder,
    write_file_utf8,
)
from personal_python_ast_optimizer.parser.config import (
    OptimizationsConfig,
    SkipConfig,
    TokensConfig,
    TokenTypesConfig,
    TypeHintsToSkip,
)
from personal_python_ast_optimizer.parser.run import run_unparser
from personal_python_ast_optimizer.regex.replace import (
    RegexReplacement,
    re_replace,
    re_replace_file,
)

from compile_utils.code_to_skip import (
    classes_to_skip,
    decorators_to_always_skip,
    decorators_to_skip,
    dict_keys_to_skip,
    from_imports_to_skip,
    functions_to_always_skip,
    functions_to_skip,
    imports_to_skip,
    module_vars_to_fold,
    no_warn_tokens,
    regex_to_apply_py,
    regex_to_apply_tk,
    vars_to_fold,
    vars_to_skip,
)
from compile_utils.log import LOGGER_NAME
from compile_utils.validation import get_required_python_version

SEPARATORS = r"[\\/]" if os.name == "nt" else r"[/]"

# Ensure this file is git ignored
MINIFIER_FAILED_FILE_NAME: str = "minifier_failure.py.example"

_logger = getLogger(LOGGER_NAME)


def clean_file_and_copy(
    path: str,
    new_path: str,
    module_name: str,
    module_import_path: str,
    assume_this_machine: bool,
) -> None:
    """Given a python file path,
    applies regexes/skips/minification and writes results to new_path"""

    source: str = read_file_utf8(path)

    if module_import_path in regex_to_apply_py:
        regex_replacements: list[RegexReplacement] = regex_to_apply_py.pop(
            module_import_path
        )
        source = re_replace(source, regex_replacements, True)

    all_vars_to_fold: dict[str, str | bytes | bool | int | float | complex | None] = (
        module_vars_to_fold.get(module_name, {})
        | vars_to_fold.pop(module_import_path, {})
    )

    try:
        source = run_unparser(
            source,
            skip_config=SkipConfig(
                module_import_path,
                target_python_version=get_required_python_version(),
                tokens_config=_get_tokens_to_skip_config(module_import_path),
                token_types_config=TokenTypesConfig(
                    skip_type_hints=TypeHintsToSkip.ALL,
                    skip_asserts=True,
                    skip_overload_functions=True,
                ),
                optimizations_config=OptimizationsConfig(
                    vars_to_fold=all_vars_to_fold,
                    collection_concat_to_unpack=True,
                    assume_this_machine=assume_this_machine,
                    simplify_named_tuples=True,
                ),
            ),
        )
    except Exception:
        _logger.exception(
            "Error when running minifier on file %s, writing source to %s",
            module_import_path,
            MINIFIER_FAILED_FILE_NAME,
        )
        write_file_utf8(MINIFIER_FAILED_FILE_NAME, source)
        raise

    write_file_utf8(new_path, source)


def move_files_to_tmp_and_clean(
    source_dir: str,
    tmp_dir: str,
    module_name: str,
    assume_this_machine: bool,
    modules_to_skip: set[str] | None = None,
) -> None:
    """Moves python files from source_dir to temp_dir
    and removes unused/unneeded code"""
    if modules_to_skip:
        modules_to_skip_re = rf"^({'|'.join(modules_to_skip)})($|\.)"
    else:
        modules_to_skip_re = ""

    for relative_file_path in _get_files_in_folder_with_filter(
        source_dir, (".py", ".pyd", ".so")
    ):
        python_file = os.path.join(source_dir, relative_file_path)
        relative_path: str = python_file.replace(source_dir, "").strip("/\\")
        module_import_path: str = sub(SEPARATORS, ".", f"{module_name}.{relative_path}")
        module_import_path = module_import_path[:-3]  # chops .py

        relative_path = os.path.join(module_name, relative_path)

        new_path: str = os.path.join(tmp_dir, relative_path)

        if modules_to_skip is not None and (
            skip_match := re.match(modules_to_skip_re, module_import_path)
        ):
            match: str = skip_match.string[: skip_match.end()]
            if match[-1:] == ".":
                match = match[:-1]
            if match in modules_to_skip:
                modules_to_skip.remove(match)
            continue

        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        if python_file.endswith(".py"):
            clean_file_and_copy(
                python_file,
                new_path,
                module_name,
                module_import_path,
                assume_this_machine,
            )
        else:
            copy_file(python_file, new_path)

    if modules_to_skip:
        _logger.warning(
            "Some modules were marked to skip but were not found: %s",
            ", ".join(modules_to_skip),
        )


def warn_unused_code_skips() -> None:
    """If any values remain from code_to_skip imports, warn
    that they were unused"""
    for skips, friendly_name in (
        (classes_to_skip, "skip classes"),
        (decorators_to_skip, "skip decorators"),
        (dict_keys_to_skip, "skip dictionary Keys"),
        (from_imports_to_skip, "skip from imports"),
        (imports_to_skip, "skip module imports"),
        (functions_to_skip, "skip functions"),
        (vars_to_fold, "fold variables"),
        (vars_to_skip, "skip variables"),
        (regex_to_apply_py, "apply regex"),
    ):
        for module in skips:
            _logger.warning(
                "Asked to %s in module %s, but was not found",
                friendly_name,
                module,
            )


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

    # strip various things in tcl files
    comments = RegexReplacement(pattern=r"^\s*#.*", flags=re.MULTILINE, count=0)
    whitespace_around_newlines = RegexReplacement(
        pattern=r"\n\s+", replacement="\n", count=0
    )
    consecutive_whitespace = RegexReplacement(
        pattern="[ \t][ \t]+", replacement=" ", count=0
    )
    prints = RegexReplacement(pattern="^(puts|parray) .*", flags=re.MULTILINE, count=0)
    extra_new_lines = RegexReplacement(pattern="\n\n+", replacement="\n", count=0)
    starting_new_line = RegexReplacement(pattern="^\n", count=1)
    whitespace_between_brackets = RegexReplacement(
        pattern="}\n}", replacement="}}", count=0
    )

    for code_file in _get_files_in_folder_with_filter(compile_dir, (".tcl", ".tm")):
        re_replace_file(
            code_file,
            [
                comments,
                whitespace_around_newlines,
                consecutive_whitespace,
                prints,
                extra_new_lines,
                starting_new_line,
                whitespace_between_brackets,
            ],
        )

    re_replace_file(
        os.path.join(compile_dir, "tcl/tclIndex"),
        whitespace_around_newlines,
        raise_if_not_applied=True,
    )


def strip_files(compile_dir: str) -> None:
    """Runs strip on all exe/dll files in provided dir"""

    # TODO: Had issues adding .so here on linux. Should be revisited here at some point
    for strippable_file in _get_files_in_folder_with_filter(
        compile_dir, (".exe", ".dll", ".pyd")
    ):
        result = subprocess.run(["strip", "--strip-all", strippable_file], check=False)  # noqa: S607

        if result.returncode != 0:
            _logger.warning("Failed to strip file %s", strippable_file)


def _get_tokens_to_skip_config(module_import_path: str) -> TokensConfig:
    classes: set[str] = classes_to_skip.pop(module_import_path, set())
    decorators: set[str] = decorators_to_skip.pop(module_import_path, set())
    dict_keys: set[str] = dict_keys_to_skip.pop(module_import_path, set())
    from_imports: set[str] = from_imports_to_skip.pop(module_import_path, set())
    module_imports: set[str] = imports_to_skip.pop(module_import_path, set())
    functions: set[str] = functions_to_skip.pop(module_import_path, set())
    variables: set[str] = vars_to_skip.pop(module_import_path, set())

    decorators |= decorators.union(decorators_to_always_skip)
    functions |= functions.union(functions_to_always_skip)

    return TokensConfig(
        classes_to_skip=classes,
        decorators_to_skip=decorators,
        dict_keys_to_skip=dict_keys,
        from_imports_to_skip=from_imports,
        module_imports_to_skip=module_imports,
        functions_to_skip=functions,
        variables_to_skip=variables,
        no_warn=no_warn_tokens,
    )


def _get_files_in_folder_with_filter(
    folder_path: str, extension_filter: tuple[str, ...]
) -> Iterator[str]:
    """Gets files in a folder and subfolders that end with certain extensions."""
    return iter(p for p in walk_folder(folder_path) if p.endswith(extension_filter))
