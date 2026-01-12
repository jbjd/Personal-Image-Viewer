"""Utilities that are OS generic."""

import os
import sys
from collections.abc import Iterator

FILE_NAME_MAX_LEN: int = 40

if os.name == "nt":
    from ctypes import windll  # type: ignore[attr-defined]

    from image_viewer.util._os_nt import get_files_in_folder as _get_files_in_folder_nt
    from image_viewer.util._os_nt import restore_file as _restore_file_nt
    from image_viewer.util._os_nt import set_hwnd as _set_hwnd
    from image_viewer.util._os_nt import trash_file as _trash_file_nt

    hwnd: int = 0

    # TODO: Move windows popups to C code
    def set_hwnd(new_hwnd: int) -> None:
        global hwnd  # noqa: PLW0603

        _set_hwnd(new_hwnd)
        hwnd = new_hwnd

    def os_name_compare(a: str, b: str) -> bool:
        return windll.shlwapi.StrCmpLogicalW(a, b) < 0

    def get_files_in_folder(folder_path: str) -> Iterator[str]:
        files: list[str] = _get_files_in_folder_nt(folder_path)
        return iter(files)

else:  # assume linux for now
    import re
    from configparser import ConfigParser
    from configparser import Error as ConfigParserError
    from tkinter.messagebox import askyesno, showinfo

    from send2trash.plat_other import HOMETRASH, send2trash

    TRASH_INFO: str = f"{HOMETRASH}/info/"

    def os_name_compare(a: str, b: str) -> bool:
        return a < b

    # TODO: Port this to C and see if its faster
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
                deleted_file_name: str = file[:-10]  # Chop .trashinfo
                path_to_trashed_file: str = f"{HOMETRASH}/files/{deleted_file_name}"

                # trashinfo file may exist, but actual file does not
                if os.path.exists(path_to_trashed_file):
                    os.rename(path_to_trashed_file, original_path)
                    os.remove(info_path)
                    break  # TODO: restore oldest first?

                os.remove(info_path)

    def _get_trashinfo_regex(path: str) -> re.Pattern:
        """Returns a regex to detect if trashinfo files could contain
        info for the provided path.

        :param path: A path to build the regex off of.
        :returns: A compiled regex to match against trashinfo files."""

        name_start: int = path.rfind("/")
        name_and_suffix: str = path if name_start == -1 else path[name_start + 1 :]

        file_name, file_suffix = _split_file_and_suffix_for_trashinfo(name_and_suffix)
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

    def _split_file_and_suffix_for_trashinfo(file_name: str) -> tuple[str, str]:
        """Given a file name, return the name and the suffix separately
        where the suffix starts at the first dot.

        :param name_and_suffix: A file name.
        :returns: The name and suffix"""
        suffix_start: int = file_name.find(".")
        return _split_str_at_index(file_name, suffix_start)

    def get_files_in_folder(folder_path: str) -> Iterator[str]:
        """Yields each file in a folder. Edited version of OS module implementation.

        :params folder_path: A path to a folder.
        :returns: The iterator over that folder."""

        with os.scandir(folder_path) as scandir_iter:
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


def show_info(title: str, body: str) -> None:
    """Shows popup with a message.

    :param title: The title of the popup
    :param body: The body of the popup"""
    if os.name == "nt":
        windll.user32.MessageBoxW(hwnd, body, title, 0)
    else:
        showinfo(title, body)


def ask_yes_no(title: str, body: str) -> None:
    """Shows popup with a message and yes/no buttons.

    :param title: The title of the popup
    :param body: The body of the popup
    :returns: True if user said yes"""
    if os.name == "nt":
        windll.user32.MessageBoxW(hwnd, body, title, 0x4)
    else:
        askyesno(title, body)


def get_byte_display(size_in_bytes: int) -> str:
    """Given a size in bytes, formats it using kb or mb.

    :param size_in_bytes: A byte size to display.
    :returns: The formatted representation of the byte value."""
    kb_size: int = 1024 if os.name == "nt" else 1000
    size_in_kb: int = size_in_bytes // kb_size
    return f"{size_in_kb / kb_size:.2f}mb" if size_in_kb > 999 else f"{size_in_kb}kb"


def trash_file(path: str) -> None:
    """OS generic way to send files to trash.

    :param path: A path to trash."""
    if os.name == "nt":
        _trash_file_nt(path)
    else:
        send2trash(path)


def restore_file(path: str) -> None:
    """OS generic way to restore a file from trash.

    :param path: A path to restore."""
    if os.name == "nt":
        _restore_file_nt(path)
    else:
        _restore_file_linux(path)


def get_normalized_folder_name(path: str) -> str:
    """Normalizes a folders name.

    :param path: A path.
    :returns: Normalized version of the path."""
    dir_name: str = os.path.dirname(path)

    # normpath of empty string returns "."
    return os.path.normpath(dir_name) if dir_name != "" else ""


def maybe_truncate_long_name(file_name: str) -> str:
    """Given a file name, return a truncated version if its too long.

    :param file_name: A file name to check.
    :returns: The original file name or a truncated version."""
    name, suffix = split_name_and_suffix(file_name)

    return (
        file_name
        if len(name) <= FILE_NAME_MAX_LEN
        else f"{name[:FILE_NAME_MAX_LEN]}(…){suffix}"
    )


def split_name_and_suffix(file_name: str) -> tuple[str, str]:
    """Given a file name, return the name and the suffix separately
    where the suffix starts at the last dot.

    :param file_name: A file name.
    :returns: The name and suffix"""
    suffix_start: int = file_name.rfind(".")
    return _split_str_at_index(file_name, suffix_start)


def _split_str_at_index(to_split: str, index: int) -> tuple[str, str]:
    """Given a string, return two strings split of the original.

    :param to_split: A string to split.
    :param index: An index to split the string at.
    :returns: The string up to index and the string at and after index."""
    return (to_split, "") if index == -1 else (to_split[:index], to_split[index:])


def get_path_to_exe_folder() -> str:
    """Returns the folder path containing the file running the program.

    :returns: The folder path."""
    return os.path.dirname(sys.argv[0])
