import os
import sys
import warnings

from nuitka.options.CommandLineOptionsTools import OurOptionGroup
from nuitka.plugins.PluginBase import NuitkaPluginBase
from nuitka.utils.ModuleNames import ModuleName

_removable_std_modules = {
    "__hello__",
    "__phello__",
    "_aix_support",
    "_markupbase",
    "_pylong",
    "cgi",
    "cgitb",
    "chunk",
    "cmd",
    "difflib",
    "filecmp",
    "fileinput",
    "ftplib",
    "html",
    "imaplib",
    "imghdr",
    "ipaddress",
    "json",
    "mailcap",
    "mimetypes",
    "modulefinder",
    "netrc",
    "nturl2path",
    "pickletools",
    "pipes",
    "pkgutil",
    "platform",
    "poplib",
    "pprint",
    "pstats",
    "pyclbr",
    "rlcompleter",
    "sched",
    "shlex",
    "sndhdr",
    "socketserver",
    "sysconfig",
    "timeit",
    "tomllib",
    "trace",
    "uu",
    "webbrowser",
    "xdrlib",
}

if sys.platform != "darwin":
    _removable_std_modules.add("_osx_support")
    if sys.platform == "win32":
        _removable_std_modules.add("configparser")

if sys.version_info >= (3, 13):
    deprecated_std_modules: set[str] = {
        "cgi",
        "cgitb",
        "chunk",
        "imghdr",
        "mailcap",
        "pipes",
        "sndhdr",
        "uu",
        "xdrlib",
    }
    if deprecated_std_modules & _removable_std_modules:
        raise NotImplementedError(
            f"Need to remove deprecated modules: {deprecated_std_modules}"
        )

if sys.version_info >= (3, 19):
    deprecated_std_modules: set[str] = {
        "nturl2path",
    }
    if deprecated_std_modules & _removable_std_modules:
        raise NotImplementedError(
            f"Need to remove deprecated modules: {deprecated_std_modules}"
        )


_removable_std_extensions: set[str] = set()

if sys.platform == "win32":
    _removable_std_extensions.add("_wmi.pyd")

_removable_dlls: set[str] = set()

if sys.platform == "win32":
    # Dependency of _wmi.pyd
    _removable_dlls.add("vcruntime140_1.dll")


class PivNuitkaPlugin(NuitkaPluginBase):  # type: ignore[misc]
    plugin_name: str = "PivPlugin"

    __slots__ = (
        "_removed_dlls",
        "_removed_std_extensions",
        "_removed_std_modules",
        "extra_checks",
        "piv_arguments",
    )

    def __init__(self, extra_checks: bool, piv_arguments: str) -> None:
        self.extra_checks: bool = extra_checks
        self.piv_arguments: str = piv_arguments
        self._removed_std_modules: set[str] = set()
        self._removed_std_extensions: set[str] = set()
        self._removed_dlls: set[str] = set()

    @classmethod
    def addPluginCommandLineOptions(cls, group: OurOptionGroup) -> None:
        group.add_option(
            "--extra-checks",
            action="store_true",
            dest="extra_checks",
            default=False,
            help="Adds extra warning logs",
        )
        group.add_option(
            "--piv-arguments",
            action="store",
            dest="piv_arguments",
            default="",
            help="Adds arguments passed to PIV to the compilation report",
        )

    def onModuleSourceCode(
        self,
        module_name: ModuleName,
        source_filename: str,  # noqa: ARG002
        source_code: str,
    ) -> str:
        # Nuitka does not allow you to skip over std modules currently, but many are
        # unused entirely and not required. As a workaround, we can use this function to
        # turn their source code into nothing
        if module_name in _removable_std_modules:
            self._removed_std_modules.add(module_name)
            return ""

        package_name: str = module_name.getPackageName()
        if package_name in _removable_std_modules:
            self._removed_std_modules.add(package_name)
            return ""

        return source_code

    def onStandaloneDistributionFinished(self, dist_dir: str) -> None:

        for extension in _removable_std_extensions:
            extension_path: str = os.path.join(dist_dir, extension)
            if os.path.exists(extension_path):
                os.remove(extension_path)
                self._removed_std_extensions.add(extension)

        for dll in _removable_dlls:
            dll_path: str = os.path.join(dist_dir, dll)
            if os.path.exists(dll_path):
                os.remove(dll_path)
                self._removed_dlls.add(dll)

        if self.extra_checks:
            prefix: str = self.plugin_name + " unable to find"

            not_found_std_modules: set[str] = (
                _removable_std_modules ^ self._removed_std_modules
            )
            if not_found_std_modules:
                warnings.warn(
                    f"{prefix} std modules to truncate: {not_found_std_modules}",
                    stacklevel=1,
                )

            not_found_extensions: set[str] = (
                _removable_std_extensions ^ self._removed_std_extensions
            )
            if not_found_extensions:
                warnings.warn(
                    f"{prefix} extension modules to remove: {not_found_extensions}",
                    stacklevel=1,
                )

            not_found_dlls: set[str] = _removable_dlls ^ self._removed_dlls
            if not_found_dlls:
                warnings.warn(
                    f"{prefix} dlls to remove: {not_found_dlls}",
                    stacklevel=1,
                )

    def getReportData(self) -> set[tuple[str, str]]:
        """Provide dictionary of data for reporting purposes."""
        # Virtual method, pylint: disable=no-self-use
        return {
            ("piv_arguments", self.piv_arguments),
            ("removed_std_modules", ",".join(self._removed_std_modules)),
            ("removed_std_extensions", ",".join(self._removed_std_extensions)),
            ("removed_dlls", ",".join(self._removed_dlls)),
        }
