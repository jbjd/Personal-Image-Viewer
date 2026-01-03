"""A script to compile the image viewer into an executable file via nuitka"""

import os
import sys
from importlib.metadata import version as get_module_version
from subprocess import Popen

from personal_compile_tools.file_operations import (
    copy_file,
    copy_folder,
    delete_file,
    delete_folder,
    delete_folders,
    get_folder_size,
    read_file_utf8,
    write_file_utf8,
)
from personal_compile_tools.modules import get_module_file_path
from personal_compile_tools.validation import raise_if_not_root

from compile_utils.args import CompileArgumentParser, CompileNamespace, NuitkaArgs
from compile_utils.cleaner import (
    clean_file_and_copy,
    clean_tk_files,
    move_files_to_tmp_and_clean,
    strip_files,
    warn_unused_code_skips,
)
from compile_utils.code_to_skip import SKIP_ITERATION
from compile_utils.constants import BUILD_INFO_FILE, IMAGE_VIEWER_NAME
from compile_utils.log import setup_logging
from compile_utils.module_dependencies import (
    get_normalized_module_name,
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

TARGET_MODULE: str = "main"
TARGET_FILE: str = f"{TARGET_MODULE}.py"

working_folder: str = os.path.normpath(os.path.dirname(__file__))
tmp_folder: str = os.path.join(working_folder, "tmp")
target_file_path: str = os.path.join(tmp_folder, TARGET_FILE)
custom_nuitka_folder_path: str = os.path.join(working_folder, "nuitka")
code_folder_path: str = os.path.join(working_folder, IMAGE_VIEWER_NAME)
compile_folder_path: str = os.path.join(working_folder, f"{TARGET_MODULE}.dist")
build_folder_path: str = os.path.join(working_folder, f"{TARGET_MODULE}.build")

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

_logger = setup_logging()

os.makedirs(tmp_folder, exist_ok=True)
try:
    clean_file_and_copy(
        f"{working_folder}/{TARGET_FILE}",
        target_file_path,
        IMAGE_VIEWER_NAME,
        f"{IMAGE_VIEWER_NAME}.{TARGET_MODULE}",
        args.assume_this_machine,
    )
    move_files_to_tmp_and_clean(
        code_folder_path,
        tmp_folder,
        IMAGE_VIEWER_NAME,
        args.assume_this_machine,
    )

    warn_unused_skips: bool = True

    minifier_version: str = get_module_version("personal_python_ast_optimizer")
    for module in module_dependencies:
        cleaned_module_iteration: str = (
            get_module_version(module.name)
            + "-"
            + minifier_version
            + f"-{SKIP_ITERATION}"
            + f"-AssumeThisMachine:{args.assume_this_machine}"
        )
        cached_iteration_path: str = os.path.join(tmp_folder, module.name) + ".txt"

        try:
            cached_iteration: str = read_file_utf8(cached_iteration_path)
        except FileNotFoundError:
            pass
        else:
            if cached_iteration == cleaned_module_iteration:
                _logger.info("Using cached version of module: %s", module.name)
                warn_unused_skips = False
                continue

        _logger.info("Setting up module: %s", module.name)

        module_import_name: str = get_normalized_module_name(module)
        sub_modules_to_skip: set[str] = set(
            i for i in modules_to_skip if i.startswith(module_import_name)
        )

        module_file_path: str = get_module_file_path(module_import_name)
        module_file: str = os.path.basename(module_file_path)
        module_folder_path: str = os.path.dirname(module_file_path)

        if module_import_name == "PIL" and os.name != "nt":
            site_packages_path = os.path.dirname(module_folder_path)
            old_lib_path: str = os.path.join(site_packages_path, "pillow.libs")
            new_lib_path: str = os.path.join(tmp_folder, "pillow.libs")
            delete_folder(new_lib_path)
            copy_folder(old_lib_path, new_lib_path)

        if module_folder_path.endswith("site-packages"):  # Its one file
            clean_file_and_copy(
                module_file_path,
                os.path.join(tmp_folder, module_file),
                module_import_name,
                module_import_name,
                args.assume_this_machine,
            )
        else:  # Its a folder
            delete_folder(os.path.join(tmp_folder, module_import_name))
            move_files_to_tmp_and_clean(
                module_folder_path,
                tmp_folder,
                module_import_name,
                args.assume_this_machine,
                sub_modules_to_skip,
            )

        write_file_utf8(cached_iteration_path, cleaned_module_iteration)

    if warn_unused_skips:
        warn_unused_code_skips()

    if args.skip_nuitka:
        sys.exit(0)

    delete_folder(compile_folder_path)

    process: Popen = start_nuitka_compilation(
        target_file_path, nuitka_args, working_folder, args.assume_this_machine
    )

    _logger.info("Waiting for nuitka compilation...")

    install_path: str = args.install_path if not args.debug else compile_folder_path

    if process.wait():
        sys.exit(1)

    for data_file_path in files_to_include:
        old_path = os.path.join(working_folder, data_file_path)
        new_path = os.path.join(compile_folder_path, data_file_path)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        copy_file(old_path, new_path)

    if args.build_info_file:
        with open(
            os.path.join(compile_folder_path, BUILD_INFO_FILE), "w", encoding="utf-8"
        ) as fp:
            fp.write(f"OS: {os.name}\n")
            fp.write(f"Python: {sys.version}\n")
            fp.write("Dependencies:\n")
            for module in module_dependencies:
                name: str = module.name
                fp.write(f"\t{name}: {get_module_version(name)}\n")
            fp.write(f"Arguments: {args}\n")

    clean_tk_files(compile_folder_path)
    if args.strip:
        strip_files(compile_folder_path)

    if not args.debug:
        delete_folder(install_path)
        os.rename(compile_folder_path, install_path)
finally:
    if not args.debug and not args.no_cleanup:
        delete_folders([build_folder_path, compile_folder_path, tmp_folder])
        delete_file(os.path.join(working_folder, f"{TARGET_MODULE}.cmd"))

_logger.info("\nFinished")
_logger.info("Installed to %s", install_path)

install_byte_size: int = get_folder_size(install_path)
_logger.info("Install Size: %s bytes", f"{install_byte_size:,}")
