from nuitka.plugins.PluginBase import NuitkaPluginBase
from personal_compile_tools.file_operations import write_file_utf8
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
)

from compile_utils.code_to_skip import (
    classes_to_skip,
    decorators_to_always_skip,
    decorators_to_skip,
    dict_keys_to_skip,
    functions_to_always_skip,
    functions_to_skip,
    imports_to_skip,
    module_vars_to_fold,
    no_warn_tokens,
    regex_to_apply_py,
    unused_imports_to_preserve,
    vars_to_fold,
    vars_to_skip,
)
from compile_utils.constants import DEV_ONLY_MESSAGE
from compile_utils.log import get_logger
from compile_utils.validation import get_required_python_version

CACHE_FOLDER: str = "build/src"
MINIFIER_FAILED_FILE_NAME: str = "minifier_failure.py.example"

_logger = get_logger()


def _get_tokens_to_skip_config(module_import_path: str) -> TokensConfig:
    classes: set[str] = classes_to_skip.pop(module_import_path, set())
    decorators: set[str] = decorators_to_skip.pop(module_import_path, set())
    dict_keys: set[str] = dict_keys_to_skip.pop(module_import_path, set())
    module_imports: set[str] = imports_to_skip.pop(module_import_path, set())
    functions: set[str] = functions_to_skip.pop(module_import_path, set())
    variables: set[str] = vars_to_skip.pop(module_import_path, set())

    decorators |= decorators.union(decorators_to_always_skip)
    functions |= functions.union(functions_to_always_skip)

    return TokensConfig(
        classes_to_skip=classes,
        decorators_to_skip=decorators,
        dict_keys_to_skip=dict_keys,
        module_imports_to_skip=module_imports,
        functions_to_skip=functions,
        variables_to_skip=variables,
        no_warn=no_warn_tokens,
    )


def clean_source(
    source: str,
    module_import_path: str,
    assume_this_machine: bool,  # TODO
) -> str:
    """Given python source code,
    applies regexes/skips/minification and returns new result."""

    if module_import_path in regex_to_apply_py:
        regex_replacements: list[RegexReplacement] = regex_to_apply_py.pop(
            module_import_path
        )
        try:
            source = re_replace(source, regex_replacements, True)
        except RegexNoMatchException as e:
            raise RuntimeError(f"Failed to apply regex to {module_import_path}") from e

    split_module: list[str] = module_import_path.split(".", maxsplit=1)
    module_name: str = split_module[0] if len(split_module) > 1 else ""
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
                    unused_imports_to_preserve=unused_imports_to_preserve.pop(
                        module_import_path, set()
                    ),
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

    return source


class PivNuitkaPlugin(NuitkaPluginBase):
    # Derive from filename, but can and should also be explicit.
    plugin_name = "PivPlugin"

    __slots__ = (
        "assume_this_machine",
        "cached_modules",
        "extra_checks",
    )

    def __init__(self, assume_this_machine: bool, extra_checks: bool) -> None:
        self.assume_this_machine: bool = assume_this_machine
        self.extra_checks: bool = extra_checks
        self.cached_modules: set[str] = set()

    @classmethod
    def addPluginCommandLineOptions(cls, group) -> None:  # noqa: ANN001
        group.add_option(
            "--assume-this-machine",
            action="store_true",
            dest="assume_this_machine",
            default=False,
            help="Allows optimizations if code will only run on this machine.",
        )
        group.add_option(
            "--extra-checks",
            action="store_true",
            dest="extra_checks",
            default=False,
            help=(
                "Adds logging around unused labels for skippable code."
                + DEV_ONLY_MESSAGE
            ),
        )

    def onModuleSourceCode(
        self,
        module_name: str,
        source_filename: str,  # noqa: ARG002
        source_code: str,
    ) -> str:
        # Never cache piv files since they will change during dev
        if not module_name.startswith("image_viewer"):
            pass

        return clean_source(source_code, module_name, self.assume_this_machine)

    def onFinalResult(self, filename: str) -> None:  # noqa: ARG002
        if not self.extra_checks:
            return

        for skips, action in (
            (classes_to_skip, "skip classes"),
            (decorators_to_skip, "skip decorators"),
            (dict_keys_to_skip, "skip dictionary Keys"),
            (imports_to_skip, "skip module imports"),
            (functions_to_skip, "skip functions"),
            (vars_to_fold, "fold variables"),
            (vars_to_skip, "skip variables"),
            (regex_to_apply_py, "apply regex"),
        ):
            for module in skips:
                if module not in self.cached_modules:
                    _logger.warning(
                        "Asked to %s in module %s, but was not found",
                        action,
                        module,
                    )
