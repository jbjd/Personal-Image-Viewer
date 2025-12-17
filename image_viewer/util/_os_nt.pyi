"""C extensions that interact with the Windows API."""

import os

from image_viewer.image._read import CMemoryViewBuffer

if os.name == "nt":
    def set_hwnd(hwnd: int, /) -> None:
        """Sets the hwnd value for all functions called in this module.

        :param hwnd: The id of the window calling the functions."""

    def trash_file(file_path: str, /) -> None:
        """Moves a file to trash.

        :param file_path: The file path to trash."""

    def restore_file(file_path: str, /) -> None:
        """Restores a file from recycling bin.

        :param file_path: The file path to restore."""

    def open_with(file_path: str, /) -> None:
        """Calls SHOpenWithDialog without registration option
        on provided file.

        :param file_path: The file path to use."""

    def drop_file_to_clipboard(file_path: str, /) -> None:
        """Copies a file to clipboard as an HDROP.

        :param file_path: The file path to drop to clipboard."""

    def get_files_in_folder(folder_path: str, /) -> list[str]:
        """Gets all files in a folder, not checking subfolders.

        :param folder_path: The folder path to check.
        :returns: A list of file names."""

    def read_buffer_as_base64_and_copy_to_clipboard(
        image_buffer: CMemoryViewBuffer, /
    ) -> None:
        """Given an image buffer, converts it to base64 and copies it to clipboard.

        :param image_buffer: The image buffer to convert."""
