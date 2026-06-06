import os
import sys
import warnings

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
    "json",
    "mailcap",
    "mimetypes",
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
    raise NotImplementedError(
        "cgi, cgitb, chunk, mailcap, sndhdr, pipes, and uu "
        "need to be removed from _removable_std_modules"
    )


_removable_extensions: set[str] = set()

if sys.platform == "win32":
    _removable_extensions.add("_wmi.pyd")

_removable_dlls: set[str] = set()

if sys.platform == "win32":
    # Dependency of _wmi.pyd
    _removable_dlls.add("vcruntime140_1.dll")


class PivNuitkaPlugin(NuitkaPluginBase):
    plugin_name: str = "PivPlugin"

    __slots__ = ("_removed_std_modules", "extra_checks")

    def __init__(self, extra_checks: bool) -> None:
        self.extra_checks: bool = extra_checks
        self._removed_std_modules: set[str] = set()

    @classmethod
    def addPluginCommandLineOptions(cls, group) -> None:  # noqa: ANN001
        group.add_option(
            "--extra-checks",
            action="store_true",
            dest="extra_checks",
            default=False,
            help="",
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

        removed_extensions: set[str] = set()

        for extension in _removable_extensions:
            path: str = os.path.join(dist_dir, extension)
            if os.path.exists(path):
                os.remove(path)
                removed_extensions.add(extension)

        removed_dlls: set[str] = set()

        for dll in _removable_dlls:
            path: str = os.path.join(dist_dir, dll)
            if os.path.exists(path):
                os.remove(path)
                removed_dlls.add(dll)

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

            not_found_extensions: set[str] = _removable_extensions ^ removed_extensions
            if not_found_extensions:
                warnings.warn(
                    f"{prefix} extension modules to remove: {not_found_extensions}",
                    stacklevel=1,
                )

            not_found_dlls: set[str] = _removable_dlls ^ removed_dlls
            if not_found_dlls:
                warnings.warn(
                    f"{prefix} dlls to remove: {not_found_dlls}",
                    stacklevel=1,
                )
