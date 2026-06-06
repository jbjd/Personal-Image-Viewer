"""A script to compile the image viewer into an executable file via nuitka"""

import os
import sys
from importlib.metadata import version as get_module_version
from subprocess import Popen

from personal_compile_tools.file_operations import (
    copy_folder,
    delete_folder,
    get_folder_size,
)
from personal_compile_tools.modules import get_module_file_path
from personal_compile_tools.validation import raise_if_not_root

from compile_utils.args import CompileArgumentParser, CompileNamespace
from compile_utils.build_setup import (
    custom_module_version_up_to_date,
    write_custom_module_version,
)
from compile_utils.cleaner import (
    clean_file_and_copy,
    clean_module_and_copy,
    clean_tk_files,
    strip_files,
    warn_unused_code_skips,
)
from compile_utils.code_to_skip import SKIP_ITERATION
from compile_utils.constants import IMAGE_VIEWER_NAME, REPORT_FILE
from compile_utils.log import get_logger
from compile_utils.module_dependencies import (
    get_normalized_module_name,
    module_dependencies,
    modules_to_skip,
)
from compile_utils.nuitka_ext import clean_compilation_report, start_nuitka_compilation
from compile_utils.validation import (
    validate_module_requirements,
    validate_PIL,
    validate_python_version,
)

working_folder: str = os.path.normpath(os.path.dirname(__file__))

files_to_include: list[str] = ["image_viewer/config.ini"]

parser = CompileArgumentParser()

args: CompileNamespace
nuitka_args: list[str]
args, nuitka_args = parser.parse_args(working_folder, files_to_include, modules_to_skip)

if not args.debug and not args.skip_nuitka:
    raise_if_not_root("Need root privileges to compile and install")

TARGET_MODULE: str = "main"
TARGET_FILE: str = f"{TARGET_MODULE}.py"

build_folder_path: str = os.path.join(working_folder, "build")
src_folder_path: str = os.path.join(build_folder_path, "src")
target_file_path: str = os.path.join(src_folder_path, TARGET_FILE)
custom_nuitka_folder_path: str = os.path.join(build_folder_path, "nuitka")
code_folder_path: str = os.path.join(working_folder, IMAGE_VIEWER_NAME)
nuitka_dist_path: str = os.path.join(build_folder_path, f"{TARGET_MODULE}.dist")
nuitka_build_path: str = os.path.join(build_folder_path, f"{TARGET_MODULE}.build")

validate_python_version()
validate_module_requirements()
validate_PIL()

_logger = get_logger()

os.makedirs(src_folder_path, exist_ok=True)
try:
    clean_file_and_copy(
        f"{working_folder}/{TARGET_FILE}",
        target_file_path,
        IMAGE_VIEWER_NAME,
        f"{IMAGE_VIEWER_NAME}.{TARGET_MODULE}",
        args.assume_this_machine,
    )
    delete_folder(os.path.join(src_folder_path, IMAGE_VIEWER_NAME))
    clean_module_and_copy(
        code_folder_path, src_folder_path, IMAGE_VIEWER_NAME, args.assume_this_machine
    )

    modules_no_warn_unused_skips: list[str] = []

    minifier_version: str = get_module_version("personal_python_ast_optimizer")
    custom_version_flags: str = (
        f"assume_this_machine={args.assume_this_machine}\n"
        f"minifier_version={minifier_version}"
    )
    for module in module_dependencies:
        module_import_name: str = get_normalized_module_name(module)

        module_file_path: str = get_module_file_path(module_import_name)
        module_file: str = os.path.basename(module_file_path)
        module_folder_path: str = os.path.dirname(module_file_path)

        is_one_file: bool = module_folder_path.rstrip("\\/").endswith("site-packages")

        module_version: str = get_module_version(module.name)
        custom_module_path: str = (
            src_folder_path
            if is_one_file
            else os.path.join(src_folder_path, module_import_name)
        )

        if custom_module_version_up_to_date(
            custom_module_path,
            module_import_name,
            module_version,
            SKIP_ITERATION,
            custom_version_flags,
        ):
            modules_no_warn_unused_skips.append(module_import_name)
            continue

        sub_modules_to_skip: set[str] = {
            i for i in modules_to_skip if i.startswith(f"{module_import_name}.")
        }

        if module_import_name == "PIL" and os.name != "nt":
            site_packages_path = os.path.dirname(module_folder_path)
            old_lib_path: str = os.path.join(site_packages_path, "pillow.libs")
            new_lib_path: str = os.path.join(src_folder_path, "pillow.libs")
            delete_folder(new_lib_path)
            copy_folder(old_lib_path, new_lib_path)

        if is_one_file:
            clean_file_and_copy(
                module_file_path,
                os.path.join(src_folder_path, module_file),
                module_import_name,
                module_import_name,
                args.assume_this_machine,
            )
        else:
            delete_folder(custom_module_path)
            clean_module_and_copy(
                module_folder_path,
                src_folder_path,
                module_import_name,
                args.assume_this_machine,
                sub_modules_to_skip,
            )

        write_custom_module_version(
            custom_module_path,
            module_import_name,
            module_version,
            SKIP_ITERATION,
            custom_version_flags,
        )

    if args.extra_checks:
        warn_unused_code_skips(modules_no_warn_unused_skips)

    if args.skip_nuitka:
        sys.exit(0)

    delete_folder(nuitka_dist_path)

    process: Popen = start_nuitka_compilation(
        target_file_path, nuitka_args, build_folder_path, args.assume_this_machine
    )

    _logger.info("Waiting for nuitka compilation...\n")

    install_path: str = args.install_path if not args.debug else nuitka_dist_path

    if process.wait():
        sys.exit(1)

    if args.report:
        clean_compilation_report(
            os.path.join(build_folder_path, REPORT_FILE), args.extra_checks
        )

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
