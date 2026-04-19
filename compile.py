"""A script to compile the image viewer into an executable file via nuitka"""

import os
import sys
from importlib.metadata import version as get_module_version
from subprocess import Popen

from personal_compile_tools.file_operations import (
    copy_file,
    delete_folder,
    get_folder_size,
)
from personal_compile_tools.validation import raise_if_not_root

from compile_utils.args import CompileArgumentParser, CompileNamespace, NuitkaArgs
from compile_utils.cleaner import clean_tk_files, strip_files
from compile_utils.constants import BUILD_INFO_FILE, IMAGE_VIEWER_NAME
from compile_utils.log import get_logger
from compile_utils.module_dependencies import (
    module_dependencies,
    modules_to_skip,
)
from compile_utils.nuitka_ext import (
    setup_custom_nuitka_install,
    start_nuitka_compilation,
)
from compile_utils.validation import (
    validate_module_requirements,
    validate_PIL,
    validate_python_version,
)

EXECUTABLE_EXT: str
DEFAULT_INSTALL_PATH: str
ICON_RELATIVE_PATH: str

if os.name == "nt":
    EXECUTABLE_EXT = ".exe"
    DEFAULT_INSTALL_PATH = "C:/Program Files/Personal Image Viewer/"
    ICON_RELATIVE_PATH = "icon/icon.ico"
else:
    EXECUTABLE_EXT = ".bin"
    DEFAULT_INSTALL_PATH = "/usr/local/personal-image-viewer/"
    ICON_RELATIVE_PATH = "icon/icon.png"

EXECUTABLE_NAME: str = "viewer" + EXECUTABLE_EXT
files_to_include: list[str] = [ICON_RELATIVE_PATH, "image_viewer/config.ini"]

parser = CompileArgumentParser(DEFAULT_INSTALL_PATH)

args: CompileNamespace
nuitka_args: list[str]
args, nuitka_args = parser.parse_known_args(modules_to_skip)

if not args.debug and not args.skip_nuitka:
    raise_if_not_root("Need root privileges to compile and install")

# Custom arg from internal nuitka plugin
if args.assume_this_machine:
    nuitka_args.append("--assume-this-machine")
if args.extra_checks:
    nuitka_args.append("--extra-checks")

TARGET_MODULE: str = "main"
TARGET_FILE: str = f"{TARGET_MODULE}.py"

working_folder: str = os.path.normpath(os.path.dirname(__file__))
build_folder_path: str = os.path.join(working_folder, "build")
src_folder_path: str = os.path.join(build_folder_path, "src")
target_file_path: str = os.path.join(src_folder_path, TARGET_FILE)
custom_nuitka_folder_path: str = os.path.join(build_folder_path, "nuitka")
code_folder_path: str = os.path.join(working_folder, IMAGE_VIEWER_NAME)
nuitka_dist_path: str = os.path.join(build_folder_path, f"{TARGET_MODULE}.dist")
nuitka_build_path: str = os.path.join(build_folder_path, f"{TARGET_MODULE}.build")

if os.name == "nt":
    nuitka_args += [
        NuitkaArgs.MINGW64,
        NuitkaArgs.WINDOWS_ICON_FROM_ICO.with_value(
            os.path.join(working_folder, ICON_RELATIVE_PATH)
        ),
    ]

setup_custom_nuitka_install(custom_nuitka_folder_path)
validate_python_version()
validate_module_requirements()
validate_PIL()

_logger = get_logger()

os.makedirs(src_folder_path, exist_ok=True)
try:
    if args.skip_nuitka:  # TODO: Move, ,maybe to onCompilationStartChecks?
        sys.exit(0)

    delete_folder(nuitka_dist_path)

    process: Popen = start_nuitka_compilation(
        target_file_path, nuitka_args, build_folder_path, args.assume_this_machine
    )

    _logger.info("Waiting for nuitka compilation...\n")

    install_path: str = args.install_path if not args.debug else nuitka_dist_path

    if process.wait():
        sys.exit(1)

    for data_file_path in files_to_include:
        old_path = os.path.join(working_folder, data_file_path)
        new_path = os.path.join(nuitka_dist_path, data_file_path)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        copy_file(old_path, new_path)

    if args.build_info_file:
        with open(
            os.path.join(nuitka_dist_path, BUILD_INFO_FILE), "w", encoding="utf-8"
        ) as fp:
            fp.write(
                f"""OS: {os.name}
Python: {sys.version}
Arguments: {args}
Dependencies:
"""
            )
            for module in module_dependencies:
                name: str = module.name
                fp.write(f"\t{name}: {get_module_version(name)}\n")

    clean_tk_files(nuitka_dist_path)
    if args.strip:
        strip_files(nuitka_dist_path)

    if not args.debug:
        delete_folder(install_path)
        os.rename(nuitka_dist_path, install_path)
finally:
    if args.no_cache:
        delete_folder(build_folder_path)

_logger.info("\nFinished")
_logger.info("Installed to %s", install_path)

install_byte_size: int = get_folder_size(install_path)
_logger.info("Install Size: %s bytes", f"{install_byte_size:,}")
