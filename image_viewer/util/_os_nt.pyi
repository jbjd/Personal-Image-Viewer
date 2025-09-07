"""C extensions that interact with the Windows API."""

import os

from image._read import CMemoryViewBuffer

if os.name == "nt":
    def trash_file(hwnd: int, file_path: str, /) -> None:
        """Moves a file to trash.

        :param hwnd: The handle of the window performing the operation.
        :param file_path: The file path to trash."""

    def restore_file(hwnd: int, file_path: str, /) -> None:
        """Restores a file from recycling bin.

        :param hwnd: The handle of the window performing the operation.
        :param file_path: The file path to restore."""

    def open_with(hwnd: int, file_path: str, /) -> None:
        """Calls SHOpenWithDialog without registration option
        on provided file.

        :param hwnd: The handle of the window performing the operation.
        :param file_path: The file path to use."""

    def drop_file_to_clipboard(hwnd: int, file_path: str, /) -> None:
        """Copies a file to clipboard as an HDROP.

        :param hwnd: The handle of the window performing the operation.
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
