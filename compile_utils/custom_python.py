import os
import sys

from personal_compile_tools.file_operations import copy_file, copy_folder, delete_folder

# Update version when we bump nuitka, python, or change logic in this file
_VERSION_FILE: str = "custom-version.txt"
_VERSION: str = "1"


def setup_custom_python(custom_folder_path: str) -> None:
    try:
        with open(
            os.path.join(custom_folder_path, _VERSION_FILE), "r", encoding="utf-8"
        ) as fp:
            if fp.read().strip() == _VERSION:
                return
    except FileNotFoundError:
        pass

    delete_folder(custom_folder_path)

    python_install_path = sys.base_prefix

    folders_to_direct_copy: list[str] = ["DLLs", "include", "libs", "tcl"]
    for folder in folders_to_direct_copy:
        old_path: str = os.path.join(python_install_path, folder)
        new_path: str = os.path.join(custom_folder_path, folder)
        copy_folder(old_path, new_path)

    old_lib_path: str = os.path.join(python_install_path, "Lib")
    new_lib_path: str = os.path.join(custom_folder_path, "Lib")
    os.makedirs(new_lib_path, exist_ok=True)

    for file_or_folder in os.listdir(old_lib_path):
        old_path: str = os.path.join(old_lib_path, file_or_folder)
        new_path: str = os.path.join(new_lib_path, file_or_folder)
        if os.path.isdir(old_path):
            if file_or_folder not in [
                "__phello__",
                "__pycache__",
                "ensurepip",
                "lib2to3",
                "site-packages",
            ]:
                copy_folder(old_path, new_path)
        else:
            if file_or_folder not in ["__hello__"]:
                copy_file(old_path, new_path)

    for file_or_folder in os.listdir(python_install_path):
        old_path: str = os.path.join(python_install_path, file_or_folder)
        if os.path.isfile(old_path) and not file_or_folder.endswith(".txt"):
            new_path: str = os.path.join(custom_folder_path, file_or_folder)
            copy_file(old_path, new_path)

    # Will not come from install path but running path to account for venv
    site_packages: list[str] = ["nuitka", "ordered_set", "zstandard"]
    for site_package in site_packages:
        old_nuitka_path: str = os.path.join(
            sys.exec_prefix, "Lib/site-packages/" + site_package
        )
        new_nuitka_path: str = os.path.join(
            custom_folder_path, "Lib/site-packages/" + site_package
        )
        copy_folder(old_nuitka_path, new_nuitka_path)

    with open(
        os.path.join(custom_folder_path, _VERSION_FILE), "w", encoding="utf-8"
    ) as fp:
        fp.write(_VERSION)
