"""Classes and functions that remove unused code and annotations"""

import os
import subprocess
from collections.abc import Iterator
from glob import glob
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
    RegexNoMatchException,
    RegexReplacement,
    re_replace,
    re_replace_file,
)
from personal_simple_tcl_minifier.parse import tcl_minify_folder

from compile_utils.code_to_skip import (
    classes_to_skip,
    decorators_to_always_skip,
    functions_to_always_skip,
    functions_to_skip,
    imports_to_skip,
    module_vars_to_fold,
    no_warn_tokens,
    regex_to_apply_py,
    regex_to_apply_tk,
    unused_imports_to_preserve,
    vars_to_fold,
    vars_to_skip,
)
from compile_utils.log import get_logger
from compile_utils.validation import get_required_python_version

SEPARATORS = r"\\/" if os.name == "nt" else r"/"

# Ensure this file is git ignored
MINIFIER_FAILED_FILE_NAME: str = "minifier_failure.py.example"

_logger = get_logger()


def _write_minify_failure(file_name: str, context_message: str, source: str) -> None:
    _logger.exception(
        "Error when %s on file %s, writing source to %s",
        context_message,
        file_name,
        MINIFIER_FAILED_FILE_NAME,
    )
    write_file_utf8(MINIFIER_FAILED_FILE_NAME, source)


def clean_file_and_copy(
    source_file_path: str,
    dest_file_path: str,
    module_name: str,
    module_import_path: str,
    assume_this_machine: bool,
) -> None:
    """Runs AST optimizer on source_file_path and writes result to dest_file_path.

    :param source_file_path: Path to clean
    :param dest_file_path: Path to write
    :param module_name: Name of module
    :param module_import_path: How the module would be imported, e.x. 'PIL.Image'
    :param assume_this_machine: Argument passed onto minifier"""

    _logger.debug("Copying %s to %s", source_file_path, dest_file_path)

    source: str = read_file_utf8(source_file_path)

    if module_import_path in regex_to_apply_py:
        regex_replacements: list[RegexReplacement] = regex_to_apply_py.pop(
            module_import_path
        )
        try:
            source = re_replace(source, regex_replacements, True)
        except RegexNoMatchException as e:
            _write_minify_failure(module_import_path, "applying regex", source)
            raise RuntimeError("Failed to apply regex to: " + module_import_path) from e

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
                    skip_generics=True,
                    skip_asserts=True,
                    skip_overload_functions=True,
                ),
                optimizations_config=OptimizationsConfig(
                    vars_to_fold=all_vars_to_fold,
                    collection_concat_to_unpack=True,
                    assume_this_machine=assume_this_machine,
                    simplify_named_tuples=True,
                    unused_imports_to_preserve=unused_imports_to_preserve.pop(
                        module_import_path, set()
                    ),
                    fold_simple_function_locals=True,
                ),
            ),
        )
    except Exception:
        _write_minify_failure(module_import_path, "running ast optimizer", source)
        raise

    write_file_utf8(dest_file_path, source)


def clean_module_and_copy(
    module_folder_path: str,
    dest_folder_path: str,
    module_name: str,
    assume_this_machine: bool,
    modules_to_skip: set[str] | None = None,
) -> None:
    """Copies all Python files of a module to dest_folder_path
    and runs AST optimizer on .py files.

    :param module_folder_path: Path to python module
    :param dest_folder_path: Path to write
    :param module_name: Name of module
    :param assume_this_machine: Argument passed onto minifier
    :param modules_to_skip: Submodules to not copy"""

    skipped_modules: set[str] = set()

    for file_path in _get_files_in_folder_with_filter(
        module_folder_path, (".py", ".pyd", ".so")
    ):
        relative_file_path: str = os.path.join(
            module_name, file_path.replace(module_folder_path, "").lstrip(SEPARATORS)
        )
        module_import_path: str = sub(f"[{SEPARATORS}]", ".", relative_file_path[:-3])

        new_file_path: str = os.path.join(dest_folder_path, relative_file_path)

        if modules_to_skip is not None and _should_skip_module(
            module_import_path, modules_to_skip, skipped_modules
        ):
            continue

        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        if file_path.endswith(".py"):
            clean_file_and_copy(
                file_path,
                new_file_path,
                module_name,
                module_import_path,
                assume_this_machine,
            )
        else:
            copy_file(file_path, new_file_path)

    if modules_to_skip is not None:
        unused_module_skips: set[str] = skipped_modules ^ modules_to_skip
        if unused_module_skips:
            _logger.warning(
                "Some modules were marked to skip but were not found: %s",
                ", ".join(unused_module_skips),
            )


def _should_skip_module(
    module_import_path: str, modules_to_skip: set[str], skipped_modules: set[str]
) -> bool:
    """Checks if a module should be skipped.

    :param module_import_path: How the module would be imported, e.x. 'PIL.Image'
    :param modules_to_skip: Set of modules, submodules will also be considered skipped
    :returns: True if module_import_path or its parent is in modules_to_skip"""
    for m in modules_to_skip:
        if module_import_path.startswith(m):
            _logger.debug("Not copying module %s", module_import_path)
            skipped_modules.add(m)
            return True

    return False


def warn_unused_code_skips(modules_no_warn_unused_skips: list[str]) -> None:
    """If any values remain from code_to_skip imports, warn
    that they were unused"""

    for skips, friendly_name in (
        (classes_to_skip, "skip classes"),
        (imports_to_skip, "skip module imports"),
        (functions_to_skip, "skip functions"),
        (vars_to_fold, "fold variables"),
        (vars_to_skip, "skip variables"),
        (regex_to_apply_py, "apply regex"),
    ):
        for module in skips:
            if all(not module.startswith(m) for m in modules_no_warn_unused_skips):
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

        re_replace_file(glob_result[0], regexes, raise_if_not_applied=True)

    tcl_minify_folder(compile_dir)


def strip_files(compile_dir: str) -> None:
    """Runs strip on all exe/dll files in provided dir"""

    # TODO: Had issues adding .so here on linux. Should be revisited here at some point
    result = subprocess.run(
        [  # noqa: S607
            "strip",
            "--strip-all",
            *_get_files_in_folder_with_filter(compile_dir, (".exe", ".dll", ".pyd")),
        ],
        check=False,
    )

    if result.returncode != 0:
        _logger.warning("Strip returned non-zero status")


def _get_tokens_to_skip_config(module_import_path: str) -> TokensConfig:
    classes: set[str] = classes_to_skip.pop(module_import_path, set())
    module_imports: set[str] = imports_to_skip.pop(module_import_path, set())
    functions: set[str] = functions_to_skip.pop(module_import_path, set())
    variables: set[str] = vars_to_skip.pop(module_import_path, set())

    functions |= functions.union(functions_to_always_skip)

    return TokensConfig(
        classes_to_skip=classes,
        decorators_to_skip=decorators_to_always_skip,
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
