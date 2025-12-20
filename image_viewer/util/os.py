"""
Code for OS specific stuff
"""

import os
import sys
from collections.abc import Iterator
from typing import Final

if os.name == "nt":
    from ctypes import windll  # type: ignore

    from image_viewer.util._os_nt import get_files_in_folder as _get_files_in_folder_nt
    from image_viewer.util._os_nt import restore_file as _restore_file_nt
    from image_viewer.util._os_nt import trash_file as _trash_file_nt

    def os_name_compare(a: str, b: str) -> bool:
        return windll.shlwapi.StrCmpLogicalW(a, b) < 0

    def get_files_in_folder(directory_path: str) -> Iterator[str]:
        files: list[str] = _get_files_in_folder_nt(directory_path)
        return iter(files)

else:  # assume linux for now
    import re
    from configparser import ConfigParser
    from configparser import Error as ConfigParserError
    from tkinter.messagebox import showinfo

    from send2trash.plat_other import HOMETRASH, send2trash

    TRASH_INFO: str = f"{HOMETRASH}/info/"

    def os_name_compare(a: str, b: str) -> bool:
        return a < b

    # TODO: break this function into smaller bits
    def _restore_file_linux(original_path: str) -> None:

        name_re: re.Pattern = _get_trashinfo_regex(original_path)

        for file in get_files_in_folder(TRASH_INFO):
            if not name_re.match(file):
                continue

            info_path: str = TRASH_INFO + file
            config_parser = ConfigParser()
            config_parser.read(info_path)

            try:
                deleted_file_original_path: str = config_parser.get(
                    "Trash Info", "Path"
                )
            except ConfigParserError:
                continue  # Malformed trashinfo

            if deleted_file_original_path == original_path:
                deleted_file_name = info_path[info_path.rfind("/info/") + 6 : -10]
                path_to_trashed_file: str = f"{HOMETRASH}/files/{deleted_file_name}"

                # trashinfo file may exist, but actual file does not
                if os.path.exists(path_to_trashed_file):
                    os.rename(path_to_trashed_file, original_path)
                    os.remove(info_path)
                    break  # TODO: restore oldest first?

    def _get_trashinfo_regex(original_path: str) -> re.Pattern:
        name_start: int = original_path.rfind("/")
        name_and_suffix: str = (
            original_path if name_start == -1 else original_path[name_start + 1 :]
        )

        file_name, file_suffix = split_name_and_suffix(name_and_suffix, False)
        # Files with same name will be test.png.trashinfo, test.2.png.trashinfo
        # or 'test 2.png.trashinfo'
        file_suffix_pattern: str = (
            rf"\{file_suffix}" if file_suffix.startswith(".") else file_suffix
        )

        # This is silly how linux handles these names
        file_name_pattern: str = (
            rf"{file_name}(( |\.)[0-9]+)?{file_suffix_pattern}\.trashinfo"
        )

        return re.compile(file_name_pattern)

    def get_files_in_folder(directory_path: str) -> Iterator[str]:
        """Copied from OS module and edited to yield each file
        and only files instead of including dirs/extra info"""

        with os.scandir(directory_path) as scandir_iter:
            while True:
                try:
                    entry = next(scandir_iter)
                except (StopIteration, OSError):
                    return

                try:
                    is_dir = entry.is_dir()
                except OSError:
                    is_dir = False

                if not is_dir:
                    yield entry.name


def show_info(hwnd: int, title: str, body: str) -> None:
    """If on Windows, shows info popup as child of parent
    Otherwise shows parent-less info popup"""
    if os.name == "nt":
        windll.user32.MessageBoxW(hwnd, body, title, 0)
    else:
        showinfo(title, body)


def get_byte_display(size_in_bytes: int) -> str:
    """Given bytes, formats it into a string using kb or mb"""
    kb_size: int = 1024 if os.name == "nt" else 1000
    size_in_kb: int = size_in_bytes // kb_size
    return f"{size_in_kb/kb_size:.2f}mb" if size_in_kb > 999 else f"{size_in_kb}kb"


def trash_file(path: str) -> None:
    """OS generic way to send files to trash"""
    if os.name == "nt":
        _trash_file_nt(path)
    else:
        send2trash(path)


def restore_file(path: str) -> None:
    """OS Generic way to restore a file from trash"""
    if os.name == "nt":
        _restore_file_nt(path)
    else:
        _restore_file_linux(path)


def get_normalized_dir_name(path: str) -> str:
    """Gets directory name of a file path and normalizes it"""
    dir_name: str = os.path.dirname(path)
    # normpath of empty string returns "."
    return os.path.normpath(dir_name) if dir_name != "" else ""


def maybe_truncate_long_name(name_and_suffix: str) -> str:
    """Takes a file name and returns a shortened version if its too long"""
    name, suffix = split_name_and_suffix(name_and_suffix)

    MAX: Final[int] = 40
    if len(name) <= MAX:
        return name_and_suffix

    return f"{name[:MAX]}(…){suffix}"


def split_name_and_suffix(name_and_suffix: str, rfind: bool = True) -> tuple[str, str]:
    """Given a file name, return the name without the suffix
    and the suffix separately"""
    suffix_start: int = (
        name_and_suffix.rfind(".") if rfind else name_and_suffix.find(".")
    )
    if suffix_start == -1:
        file_name = name_and_suffix
        suffix = ""
    else:
        file_name = name_and_suffix[:suffix_start]
        suffix = name_and_suffix[suffix_start:]

    return file_name, suffix


def get_path_to_exe_folder() -> str:
    """Returns the folder path containing the file running the program

    :returns: The folder path"""
    return os.path.dirname(sys.argv[0])
