"""Argument definitions and parsing."""

import os
from argparse import ArgumentParser, Namespace
from enum import StrEnum

from compile_utils.code_to_skip import data_files_to_exclude, dlls_to_include
from compile_utils.constants import REPORT_FILE
from compile_utils.module_dependencies import modules_to_include


class ConsoleMode(StrEnum):
    """Options for console mode in nuitka."""

    FORCE = "force"
    DISABLE = "disable"


class NuitkaArgs(StrEnum):
    """Nuitka arguments that are used as part of compilation."""

    DEPLOYMENT = "--deployment"
    STANDALONE = "--standalone"
    MINGW64 = "--mingw64"
    ENABLE_PLUGIN = "--enable-plugin"
    NO_FOLLOW_IMPORT = "--nofollow-import-to"
    INCLUDE_DATA_FILES = "--include-data-files"
    NO_INCLUDE_DATA_FILES = "--noinclude-data-files"
    INCLUDE_MODULE = "--include-module"
    NO_INCLUDE_DLLS = "--noinclude-dlls"
    WINDOWS_ICON_FROM_ICO = "--windows-icon-from-ico"
    WINDOWS_CONSOLE_MODE = "--windows-console-mode"
    REMOVE_OUTPUT = "--remove-output"
    QUIET = "--quiet"
    VERBOSE = "--verbose"
    REPORT = "--report"
    WARN_IMPLICIT_EXCEPTIONS = "--warn-implicit-exceptions"
    WARN_UNUSUAL_CODE = "--warn-unusual-code"

    def with_value(self, value: str) -> str:
        """Returns the flag in the format {flag}={value}"""
        return f"{self}={value}"


class PivArgs(StrEnum):
    INSTALL_PATH = "--install-path"
    REPORT = "--report"
    STRIP = "--strip"
    DISTRIBUTION = "--distribution"
    QUIET = "--quiet"
    VERBOSE = "--verbose"
    EXTRA_CHECKS = "--extra-checks"
    NO_CACHE = "--no-cache"
    DEBUG = "--debug"
    SKIP_NUITKA = "--skip-nuitka"


class PivPluginArgs(StrEnum):
    EXTRA_CHECKS = "--extra-checks"
    PIV_ARGS = "--piv-arguments"


class CompileNamespace(Namespace):
    """Namespace for compilation flags."""

    install_path: str
    report: bool
    debug: bool
    strip: bool
    distribution: bool
    skip_nuitka: bool
    quiet: bool
    verbose: bool
    extra_checks: bool
    no_cache: bool

    def __str__(self) -> str:
        return ", ".join(
            f"{k}={v}" for k, v in self.__dict__.items() if isinstance(v, bool)
        )


class CompileArgumentParser:
    """Argument Parser for compilation flags."""

    __slots__ = ("arg_parser",)

    def __init__(self) -> None:
        self.arg_parser = ArgumentParser(
            description="Compiles Personal Image Viewer to an executable"
        )

        default_install_path: str = (
            "C:/Program Files/Personal Image Viewer/"
            if os.name == "nt"
            else "/usr/local/personal-image-viewer/"
        )

        self.add_argument(
            PivArgs.INSTALL_PATH, "Path to install to.", default_install_path
        )
        self.add_argument(
            PivArgs.REPORT,
            f"Adds {NuitkaArgs.REPORT.with_value(REPORT_FILE)} flag to nuitka.",
        )
        self.add_argument(
            PivArgs.STRIP,
            "Calls strip on all .exe/.dll/.pyd files after compilation. "
            "Requires strip being installed and on PATH.",
        )
        self.add_argument(
            PivArgs.DISTRIBUTION,
            "Includes licenses. Remove CFLAGS -march=native and -mtune=native and "
            "disables optimization of machine general python code into machine "
            "specific code. If on Windows, also includes needed dlls.",
        )
        self.add_argument(
            PivArgs.QUIET, "Adds --quiet flag to nuitka.", is_development=True
        )
        self.add_argument(
            PivArgs.VERBOSE, "Adds --quiet flag to nuitka.", is_development=True
        )
        self.add_argument(
            PivArgs.EXTRA_CHECKS,
            "Adds extra checks during build.",
            is_development=True,
        )
        self.add_argument(
            PivArgs.NO_CACHE,
            "Removes cached parts of build process.",
            is_development=True,
        )
        self.add_argument(
            PivArgs.DEBUG,
            (
                "Doesn't move compiled code to install path, doesn't check for root, "
                "assumes --report and --extra_checks, adds "
                f"{NuitkaArgs.WARN_IMPLICIT_EXCEPTIONS}, {NuitkaArgs.WARN_UNUSUAL_CODE}"
                f", and {NuitkaArgs.WINDOWS_CONSOLE_MODE}={ConsoleMode.FORCE} "
                f"flags to nuitka."
            ),
            is_development=True,
        )
        self.add_argument(
            PivArgs.SKIP_NUITKA,
            (
                "Skips running nuitka so no compilation takes place. "
                "Only creates the tmp folder as it would be before compilation. "
                f"Disables {PivArgs.NO_CACHE} if also passed."
            ),
            is_development=True,
        )

    def add_argument(
        self,
        name: str,
        help_text: str,
        default: str | bool = False,
        is_development: bool = False,
    ) -> None:
        """Extension of add_argument to simplify repeated patterns.

        :param name: The name of the argument.
        :param: help_text: A description of what the argument does.
        :param default: The default value. Bools use store_true and strings use store.
        :param is_development: Adds to help text that flag is for dev purposes."""

        if is_development:
            help_text += " This option is exposed for development."

        if default:
            help_text += f" Defaults to {default}."

        action: str = "store_true" if isinstance(default, bool) else "store"

        self.arg_parser.add_argument(
            name, help=help_text, action=action, default=default
        )

    def parse_args(
        self,
        working_folder: str,
        files_to_include: list[str],
        modules_to_skip: list[str],
    ) -> tuple[CompileNamespace, list[str]]:
        """Returns CompileNamespace of user args and list of args to pass to nuitka"""
        args: CompileNamespace = self.arg_parser.parse_args(
            namespace=CompileNamespace()
        )

        if args.quiet and args.verbose:
            raise ValueError(f"Can't pass both {PivArgs.QUIET} and {PivArgs.VERBOSE}")

        nuitka_args: list[str] = [
            f"{PivPluginArgs.PIV_ARGS}={args}",
            NuitkaArgs.STANDALONE,
            NuitkaArgs.ENABLE_PLUGIN.with_value("tk-inter"),
        ]

        # PivPlugin args
        if args.extra_checks:
            nuitka_args.append(PivPluginArgs.EXTRA_CHECKS)

        if args.debug:
            args.report = True
            args.extra_checks = True
        else:
            nuitka_args.append(NuitkaArgs.DEPLOYMENT)
            nuitka_args.append(NuitkaArgs.REMOVE_OUTPUT)

        if args.report:
            nuitka_args.append(NuitkaArgs.REPORT.with_value(REPORT_FILE))
            if args.debug:
                nuitka_args += [
                    NuitkaArgs.WARN_IMPLICIT_EXCEPTIONS,
                    NuitkaArgs.WARN_UNUSUAL_CODE,
                ]

        if args.quiet:
            nuitka_args.append(NuitkaArgs.QUIET)
        elif args.verbose:
            nuitka_args.append(NuitkaArgs.VERBOSE)

        icon_relative_path: str = (
            "icon/icon.ico" if os.name == "nt" else "icon/icon.png"
        )
        icon_path: str = os.path.join(working_folder, icon_relative_path)

        nuitka_args.append(self._get_data_file_arg(icon_path, icon_relative_path))
        nuitka_args += [
            self._get_data_file_arg(os.path.join(working_folder, f), f)
            for f in files_to_include
        ]

        nuitka_args += [
            NuitkaArgs.NO_FOLLOW_IMPORT.with_value(module) for module in modules_to_skip
        ]
        nuitka_args += [
            NuitkaArgs.NO_INCLUDE_DATA_FILES.with_value(glob)
            for glob in data_files_to_exclude
        ]
        if not args.distribution:
            nuitka_args.append(
                NuitkaArgs.NO_INCLUDE_DATA_FILES.with_value("tk/license.terms")
            )

        nuitka_args += [
            NuitkaArgs.INCLUDE_MODULE.with_value(module)
            for module in modules_to_include
        ]

        if os.name == "nt":
            console_node: str = ConsoleMode.FORCE if args.debug else ConsoleMode.DISABLE
            nuitka_args += [
                NuitkaArgs.MINGW64,
                NuitkaArgs.WINDOWS_ICON_FROM_ICO.with_value(icon_path),
                NuitkaArgs.WINDOWS_CONSOLE_MODE.with_value(console_node),
            ]

            if args.distribution:
                nuitka_args += [
                    self._get_data_file_arg(self._get_full_path_to_file(file), file)
                    for file in (dlls_to_include)
                ]

        return args, nuitka_args

    @staticmethod
    def _get_data_file_arg(abs_path: str, rel_path: str) -> str:
        return NuitkaArgs.INCLUDE_DATA_FILES.with_value(f"{abs_path}={rel_path}")

    @staticmethod
    def _get_full_path_to_file(file: str) -> str:
        """Finds required file on $PATH.

        :param file: File name to search for.
        :returns: Full path to file."""

        path_env: str = os.environ.get("PATH", "")

        for folder in path_env.split(os.pathsep):
            if not folder:
                continue

            target: str = os.path.join(folder, file)
            if os.path.isfile(target):
                return target

        raise FileNotFoundError(f"Can't find dll file {file} on $PATH")
