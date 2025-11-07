"""A script to compile the image viewer into an executable file via nuitka"""

import os
import sys
from importlib.metadata import version as get_module_version
from subprocess import Popen

from personal_compile_tools.file_operations import (
    copy_file,
    delete_file,
    delete_folder,
    delete_folders,
    get_folder_size,
)

from compile_utils.args import CompileArgumentParser, CompileNamespace, NuitkaArgs
from compile_utils.cleaner import clean_tk_files, strip_files
from compile_utils.constants import BUILD_INFO_FILE, IMAGE_VIEWER_NAME
from compile_utils.log import setup_logging
from compile_utils.module_dependencies import module_dependencies, modules_to_skip
from compile_utils.nuitka_ext import start_nuitka_compilation
from compile_utils.validation import (
    raise_if_not_root,
    validate_module_requirements,
    validate_python_version,
)

validate_python_version()

WORKING_FOLDER: str = os.path.normpath(os.path.dirname(__file__))
TARGET_MODULE: str = "main"
TARGET_FILE: str = f"{TARGET_MODULE}.py"
TMP_FOLDER: str = os.path.join(WORKING_FOLDER, "tmp")
CODE_FOLDER: str = os.path.join(WORKING_FOLDER, IMAGE_VIEWER_NAME)
COMPILE_FOLDER: str = os.path.join(WORKING_FOLDER, f"{TARGET_MODULE}.dist")
BUILD_FOLDER: str = os.path.join(WORKING_FOLDER, f"{TARGET_MODULE}.build")

EXECUTABLE_EXT: str
DEFAULT_INSTALL_PATH: str

if os.name == "nt":
    EXECUTABLE_EXT = ".exe"
    DEFAULT_INSTALL_PATH = "C:/Program Files/Personal Image Viewer/"
else:
    EXECUTABLE_EXT = ".bin"
    DEFAULT_INSTALL_PATH = "/usr/local/personal-image-viewer/"

EXECUTABLE_NAME: str = "viewer" + EXECUTABLE_EXT
FILES_TO_INCLUDE: list[str] = []

parser = CompileArgumentParser(DEFAULT_INSTALL_PATH)

args: CompileNamespace
nuitka_args: list[str]
args, nuitka_args = parser.parse_known_args(modules_to_skip)

if not args.debug and not args.skip_nuitka:
    raise_if_not_root()

if os.name == "nt":
    nuitka_args += [NuitkaArgs.MINGW64]

_logger = setup_logging()

validate_module_requirements()

try:
    delete_folder(COMPILE_FOLDER)
    target_file_path: str = f"{WORKING_FOLDER}/{TARGET_FILE}"
    default_python: str = "python" if os.name == "nt" else "bin/python3"
    python_path: str = os.path.join(sys.exec_prefix, default_python)
    process: Popen = start_nuitka_compilation(
        python_path, target_file_path, WORKING_FOLDER, nuitka_args
    )

    _logger.info("Waiting for nuitka compilation...")

    install_path: str = args.install_path if not args.debug else COMPILE_FOLDER

    if process.wait():
        sys.exit(1)

    for data_file_path in FILES_TO_INCLUDE:
        old_path = os.path.join(WORKING_FOLDER, data_file_path)
        new_path = os.path.join(COMPILE_FOLDER, data_file_path)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        copy_file(old_path, new_path)

    clean_tk_files(COMPILE_FOLDER)
    if args.strip:
        strip_files(COMPILE_FOLDER)

    if not args.debug:
        delete_folder(install_path)
        os.rename(COMPILE_FOLDER, install_path)
finally:
    if not args.debug and not args.no_cleanup:
        delete_folders([BUILD_FOLDER, COMPILE_FOLDER, TMP_FOLDER])
        delete_file(os.path.join(WORKING_FOLDER, f"{TARGET_MODULE}.cmd"))

_logger.info("\nFinished")
_logger.info("Installed to %s", install_path)

install_byte_size: int = get_folder_size(install_path)
_logger.info("Install Size: %s bytes", f"{install_byte_size:,}")
