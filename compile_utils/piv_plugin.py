import os
import sys
import warnings

from nuitka.plugins.PluginBase import NuitkaPluginBase
from nuitka.utils.ModuleNames import ModuleName

_skippable_std_modules = {
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
    "configparser",
}

if sys.platform != "darwin":
    _skippable_std_modules.add("_osx_support")
    if sys.platform == "win32":
        _skippable_std_modules.add("configparser")

if sys.version_info >= (3, 13):
    raise NotImplementedError(
        "cgi, cgitb, chunk, mailcap, sndhdr, pipes, and uu "
        "need to be removed from _skippable_std_modules"
    )


class PivNuitkaPlugin(NuitkaPluginBase):
    plugin_name: str = "PivPlugin"

    __slots__ = (
        "_found_modules",
        "extra_checks",
    )

    def __init__(self, extra_checks: bool) -> None:
        self.extra_checks: bool = extra_checks
        self._found_modules: set[str] = set()

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

        # TODO: Just zipimport isn't caught by this and I am not sure why

        # Nuitka does not allow you to skip over std modules currently, but many are
        # unused entirely and not required. As a workaround, we can use this function to
        # turn their source code into nothing
        package_name: str = module_name.getPackageName() or module_name
        if package_name in _skippable_std_modules:
            self._found_modules.add(package_name)
            return ""

        return source_code

    def onStandaloneDistributionFinished(self, dist_dir: str) -> None:

        if sys.platform == "win32":
            # Unused but Nuitka does not provide way to exclude
            wmi_path: str = os.path.join(dist_dir, "_wmi.pyd")
            if os.path.exists(wmi_path):
                os.remove(wmi_path)

            # Dependency of _wmi
            vcruntime_path: str = os.path.join(dist_dir, "vcruntime140_1.dll")
            if os.path.exists(vcruntime_path):
                os.remove(vcruntime_path)

        if self.extra_checks:
            not_found: set[str] = _skippable_std_modules ^ self._found_modules
            if not_found:
                warnings.warn(
                    self.plugin_name
                    + f" unable to find std modules to truncate: {not_found}",
                    stacklevel=1,
                )
