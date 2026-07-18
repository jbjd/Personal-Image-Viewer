"""Classes and functions that remove unused code and annotations"""

import os
import subprocess
from collections.abc import Iterable, Iterator
from glob import glob
from re import sub

from personal_compile_tools.file_operations import (
    copy_file,
    read_file_utf8,
    walk_folder,
    write_file_utf8,
)
from personal_python_ast_optimizer.config import (
    CodeToSkipConfig,
    OptimizeConfig,
    PerfOptimizationsConfig,
    TokensToFold,
    TokensToSkip,
    TokensToSkipConfig,
    TokenTypesToSkipConfig,
    TypeHintsToSkip,
)
from personal_python_ast_optimizer.regex.replace import (
    RegexNoMatchError,
    RegexReplacement,
    re_replace,
    re_replace_file,
)
from personal_python_ast_optimizer.run import optimize_source_and_minify
from personal_python_ast_optimizer.typing import FoldableConstant
from personal_simple_tcl_minifier.parse import tcl_minify_folder

from compile_utils.code_to_skip import (
    assignments_to_skip,
    classes_to_skip,
    decorators_to_always_skip,
    foldable_constants,
    from_imports_to_skip,
    functions_to_always_skip,
    functions_to_skip,
    machine_specific_call_folds_input,
    machine_specific_folds,
    module_foldable_constants,
    regex_to_apply_py,
    regex_to_apply_tk,
    unused_imports_to_preserve,
)
from compile_utils.log import get_logger

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
        except RegexNoMatchError as e:
            _write_minify_failure(module_import_path, "applying regex", source)
            raise RuntimeError("Failed to apply regex to: " + module_import_path) from e

    try:
        source = optimize_source_and_minify(
            source,
            optimize_config=OptimizeConfig(
                code_to_skip=CodeToSkipConfig(
                    unused_imports_to_preserve=unused_imports_to_preserve.pop(
                        module_import_path, None
                    ),
                    skip_overload_functions=True,
                ),
                tokens_to_skip=_get_tokens_to_skip_config(module_import_path),
                token_types_to_skip=TokenTypesToSkipConfig(
                    skip_type_hints=TypeHintsToSkip.ALL,
                    skip_generics_and_alias=True,
                    skip_asserts=True,
                ),
                perf_optimizations=_get_perf_optimizations_config(
                    module_name, module_import_path, assume_this_machine
                ),
            ),
            file_name=module_import_path,
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
        (assignments_to_skip, "skip assignments"),
        (classes_to_skip, "skip classes"),
        (from_imports_to_skip, "skip from imports"),
        (functions_to_skip, "skip functions"),
        (foldable_constants, "fold variables"),
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


def _get_tokens_to_skip_config(module_import_path: str) -> TokensToSkipConfig:
    _warn_all: list = []

    assignments: set[str] | None = assignments_to_skip.pop(module_import_path, None)
    assignments_input: TokensToSkip[str] | None = (
        TokensToSkip(assignments, _warn_all) if assignments is not None else None
    )

    classes: set[str] | None = classes_to_skip.pop(module_import_path, None)
    classes_input: TokensToSkip[str] | None = (
        TokensToSkip(classes, _warn_all) if classes is not None else None
    )

    from_module_imports: set[tuple[str, str]] | None = from_imports_to_skip.pop(
        module_import_path, None
    )
    from_module_imports_input: TokensToSkip[tuple[str, str]] | None = (
        TokensToSkip(from_module_imports, _warn_all)
        if from_module_imports is not None
        else None
    )

    decorators_input = TokensToSkip(decorators_to_always_skip)

    functions: set[str] | None = functions_to_skip.pop(module_import_path, None)
    functions = (
        functions_to_always_skip
        if functions is None
        else functions.union(functions_to_always_skip)
    )
    functions_input: TokensToSkip[str] | None = (
        TokensToSkip(functions, functions_to_always_skip)
        if functions is not None
        else None
    )

    return TokensToSkipConfig(
        assignments_to_skip=assignments_input,
        classes_to_skip=classes_input,
        decorators_to_skip=decorators_input,
        from_imports_to_skip=from_module_imports_input,
        functions_to_skip=functions_input,
    )


def _get_perf_optimizations_config(
    module_name: str, module_import_path: str, assume_this_machine: bool
) -> PerfOptimizationsConfig:
    config = PerfOptimizationsConfig(  # TODO: Fix names_to_fold
        fold_simple_function_locals=True,
        collection_concat_to_unpack=True,
        simplify_named_tuple=True,
    )

    names_and_attrs: dict[str, FoldableConstant] = foldable_constants.pop(
        module_import_path, {}
    )
    no_warn_folds: Iterable[str]

    if module_name in module_foldable_constants:
        module_folds: dict[str, FoldableConstant] = module_foldable_constants[
            module_name
        ]
        names_and_attrs |= module_folds
        no_warn_folds = module_folds
    else:
        no_warn_folds = {}

    if assume_this_machine:
        config.calls_to_fold = machine_specific_call_folds_input
        names_and_attrs |= machine_specific_folds
        no_warn_folds |= machine_specific_folds

    config.name_or_attr_to_fold = TokensToFold(names_and_attrs, no_warn_folds)

    return config


def _get_files_in_folder_with_filter(
    folder_path: str, extension_filter: tuple[str, ...]
) -> Iterator[str]:
    """Gets files in a folder and subfolders that end with certain extensions."""
    return iter(p for p in walk_folder(folder_path) if p.endswith(extension_filter))
