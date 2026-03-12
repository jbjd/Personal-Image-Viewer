"""
Classes representing undoable actions that a user can do
"""

import os
from abc import abstractmethod
from typing import override

from image_viewer.util.os import restore_file, trash_file


class FileAction:
    """Class used to track actions done to a file"""

    __slots__ = ("original_path",)

    def __init__(self, original_path: str) -> None:
        self.original_path: str = original_path

    @abstractmethod
    def get_undo_message(self) -> str:
        """Returns message to use when undoing this action."""

    @abstractmethod
    def undo(self) -> tuple[str, str]:
        """Undoes this action by moving/deleting files to restore state before
        action occurred.

        :returns: Tuple of path restored and path removed,
        paths will be empty if unchanged"""


class Rename(FileAction):
    """Represents a file path changing"""

    __slots__ = ("new_path",)

    def __init__(self, original_path: str, new_path: str) -> None:
        super().__init__(original_path)
        self.new_path: str = new_path

    @override
    def get_undo_message(self) -> str:
        return f"Rename {self.new_path} back to {self.original_path}?"

    @override
    def undo(self) -> tuple[str, str]:
        os.rename(self.new_path, self.original_path)
        return (self.original_path, self.new_path)


class Convert(Rename):
    """Represents a conversion done to a file such that a new path exists,
    but it is related to the old path. Such as converting an image where both
    the old and converted image now exist"""

    __slots__ = ("original_file_deleted",)

    def __init__(
        self, original_path: str, new_path: str, original_file_deleted: bool = False
    ) -> None:
        super().__init__(original_path, new_path)
        self.original_file_deleted: bool = original_file_deleted

    @override
    def get_undo_message(self) -> str:
        return (
            f"Delete {self.new_path} and restore {self.original_path} from trash?"
            if self.original_file_deleted
            else f"Delete {self.new_path}?"
        )

    @override
    def undo(self) -> tuple[str, str]:
        trash_file(self.new_path)

        if self.original_file_deleted:
            restore_file(self.original_path)
            return (self.original_path, self.new_path)

        return ("", self.new_path)


class Delete(FileAction):
    """Represents a file being deleted and sent to the recycle bin"""

    __slots__ = ()

    @override
    def get_undo_message(self) -> str:
        return f"Restore {self.original_path} from trash?"

    @override
    def undo(self) -> tuple[str, str]:
        restore_file(self.original_path)
        return (self.original_path, "")
