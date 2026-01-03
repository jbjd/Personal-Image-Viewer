"""Argument definition and parsing for compilation"""

from argparse import ArgumentParser, Namespace
from enum import StrEnum

from compile_utils.code_to_skip import (
    data_files_to_exclude,
    dlls_to_exclude,
    dlls_to_include,
)
from compile_utils.constants import BUILD_INFO_FILE, REPORT_FILE
from compile_utils.module_dependencies import modules_to_include
from compile_utils.validation import get_full_path_to_dll


class ConsoleMode(StrEnum):
    """Options for console mode in nuitka"""

    FORCE = "force"
    DISABLE = "disable"


class NuitkaArgs(StrEnum):
    """Nuitka arguments that are used as part of compilation"""

    DEPLOYMENT = "--deployment"
    STANDALONE = "--standalone"
    MINGW64 = "--mingw64"
    ENABLE_PLUGIN = "--enable-plugin"
    NO_FOLLOW_IMPORT = "--nofollow-import-to"
    INCLUDE_DATA_FILES = "--include-data-files"
    NO_INCLUDE_DATA_FILES = "--noinclude-data-files"
    INCLUDE_MODULE = "--include-module"
    INCLUDE_DLLS = "--include-data-files"
    NO_INCLUDE_DLLS = "--noinclude-dlls"
    WINDOWS_ICON_FROM_ICO = "--windows-icon-from-ico"
    WINDOWS_CONSOLE_MODE = "--windows-console-mode"
    REMOVE_OUTPUT = "--remove-output"
    QUIET = "--quiet"
    VERBOSE = "--verbose"
    REPORT = "--report"
    WARN_IMPLICIT_EXCEPTIONS = "--warn-implicit-exceptions"
    WARN_UNUSUAL_CODE = "--warn-unusual-code"
    SHOW_SCONS = "--show-scons"
    SHOW_MEMORY = "--show-memory"

    def with_value(self, value: str) -> str:
        """Returns the flag in the format {flag}={value}"""
        return f"{self}={value}"


class CompileNamespace(Namespace):
    """Namespace for compilation flags"""

    install_path: str
    report: bool
    debug: bool
    strip: bool
    skip_nuitka: bool
    no_cleanup: bool
    build_info_file: bool
    user_nuitka_args: list[str]


class CompileArgumentParser(ArgumentParser):
    """Argument Parser for compilation flags"""

    __slots__ = ()

    VALID_NUITKA_ARGS: list[str] = [
        NuitkaArgs.QUIET.value,
        NuitkaArgs.VERBOSE.value,
        NuitkaArgs.SHOW_SCONS.value,
        NuitkaArgs.SHOW_MEMORY.value,
        NuitkaArgs.WINDOWS_CONSOLE_MODE.value,
    ]

    def __init__(self, install_path: str) -> None:
        super().__init__(
            description="Compiles Personal Image Viewer to an executable",
            epilog=f"Some nuitka arguments are also accepted: {self.VALID_NUITKA_ARGS}",
        )

        self.add_argument_ext(
            "--install-path",
            f"Path to install to, defaults to {install_path}",
            install_path,
        )
        self.add_argument_ext(
            "--report",
            f"Adds {NuitkaArgs.REPORT.with_value(REPORT_FILE)} flag to nuitka.",
        )
        self.add_argument_ext(
            "--build-info-file", f"Includes {BUILD_INFO_FILE} with distribution."
        )
        self.add_argument_ext(
            "--strip",
            (
                "Calls strip on all .exe/.dll/.pyd files after compilation. "
                "Requires strip being installed and on PATH."
            ),
        )
        self.add_argument_ext(
            "--debug",
            (
                "Doesn't move compiled code to install path, doesn't check for root, "
                "assumes --no-cleanup and --report, adds "
                f"{NuitkaArgs.WARN_IMPLICIT_EXCEPTIONS}, {NuitkaArgs.WARN_UNUSUAL_CODE}"
                f", and {NuitkaArgs.WINDOWS_CONSOLE_MODE}={ConsoleMode.FORCE} "
                f"flags to nuitka."
            ),
            is_debug=True,
        )
        self.add_argument_ext(
            "--skip-nuitka",
            (
                "Skips running nuitka so no compilation takes place. "
                "Only creates the tmp folder as it would be before compilation."
                "Assumes --no-cleanup however nuitka's build folder is never made "
                "so only the tmp folder is not cleaned up."
            ),
            is_debug=True,
        )
        self.add_argument_ext(
            "--no-cleanup",
            "Does not delete temporary files used for compilation/installation.",
            is_debug=True,
        )

    def add_argument_ext(
        self,
        name: str,
        help_text: str,
        default: str | bool = False,
        is_debug: bool = False,
    ) -> None:
        """Extension of add_argument to simplify repeated patterns.

        :param name: The name of the argument.
        :param: help_text: A description of what the argument does.
        :param default: The default value. Bools use store_true and strings use store.
        :param is_debug: Adds to help text that this is intended for debugging."""

        if is_debug:
            help_text += " This option is exposed for debugging."

        action: str = "store_true" if isinstance(default, bool) else "store"

        super().add_argument(name, help=help_text, action=action, default=default)

    # Override the args of the super class
    def parse_known_args(  # type: ignore # pylint: disable=arguments-differ
        self, modules_to_skip: list[str]
    ) -> tuple[CompileNamespace, list[str]]:
        """Returns CompileNamespace of user args and list of args to pass to nuitka"""
        args, nuitka_args = super().parse_known_args(namespace=CompileNamespace())
        self._validate_args(nuitka_args)

        # Preserve just what the user inputted since this list will get expanded
        args.user_nuitka_args = nuitka_args[:]
        self._expand_nuitka_args(args, nuitka_args, modules_to_skip)

        return args, nuitka_args

    def _validate_args(self, nuitka_args: list[str]) -> None:
        """Validates that all unrecognized args are part of the subset of
        nuitka args this program accepts.

        :param nuitka_args: A list of possibly valid nuitka arguments
        :raises ValueError: If any argument isn't part of that subset."""

        for extra_arg in nuitka_args:
            if extra_arg.split("=")[0] not in self.VALID_NUITKA_ARGS:
                raise ValueError(f"Unknown argument {extra_arg}")

    @staticmethod
    def _expand_nuitka_args(
        args: CompileNamespace, nuitka_args: list[str], modules_to_skip: list[str]
    ) -> None:
        """Updates nuitka_args list with all non-user controlled args
        to be passed to nuitka."""
        nuitka_args.append(NuitkaArgs.STANDALONE)

        if args.report or args.debug:
            nuitka_args.append(NuitkaArgs.REPORT.with_value(REPORT_FILE))
            if args.debug:
                nuitka_args += [
                    NuitkaArgs.WARN_IMPLICIT_EXCEPTIONS,
                    NuitkaArgs.WARN_UNUSUAL_CODE,
                ]

        if not args.debug:
            nuitka_args.append(NuitkaArgs.DEPLOYMENT)

            if not args.no_cleanup:
                nuitka_args.append(NuitkaArgs.REMOVE_OUTPUT)

        nuitka_args.append(NuitkaArgs.ENABLE_PLUGIN.with_value("tk-inter"))

        nuitka_args += [
            NuitkaArgs.NO_FOLLOW_IMPORT.with_value(module) for module in modules_to_skip
        ]
        nuitka_args += [
            NuitkaArgs.NO_INCLUDE_DATA_FILES.with_value(glob)
            for glob in data_files_to_exclude
        ]
        nuitka_args += [
            NuitkaArgs.INCLUDE_MODULE.with_value(module)
            for module in modules_to_include
        ]
        nuitka_args += [
            NuitkaArgs.INCLUDE_DATA_FILES.with_value(get_full_path_to_dll(file))
            + f"={file}"
            for file in (dlls_to_include)
        ]
        nuitka_args += [
            NuitkaArgs.NO_INCLUDE_DLLS.with_value(glob) for glob in dlls_to_exclude
        ]

        if not any(
            arg.startswith(NuitkaArgs.WINDOWS_CONSOLE_MODE) for arg in nuitka_args
        ):
            nuitka_args.append(
                NuitkaArgs.WINDOWS_CONSOLE_MODE.with_value(
                    ConsoleMode.FORCE if args.debug else ConsoleMode.DISABLE
                )
            )
