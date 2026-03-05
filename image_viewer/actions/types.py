"""
Classes representing undoable actions that a user can do
"""

from abc import abstractmethod
from typing import override


class FileAction:
    """Class used to track actions done to a file"""

    __slots__ = ("original_path",)

    @abstractmethod
    def __init__(self, original_path: str) -> None:
        self.original_path: str = original_path

    @abstractmethod
    def get_undo_message() -> str:
        """Returns message to use when undoing this action."""


class Rename(FileAction):
    """Represents a file path changing"""

    __slots__ = ("new_path",)

    def __init__(self, original_path: str, new_path: str) -> None:
        super().__init__(original_path)
        self.new_path: str = new_path

    @override
    def get_undo_message(self) -> str:
        return f"Rename {self.new_path} back to {self.original_path}?"


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


class Delete(FileAction):
    """Represents a file being deleted and sent to the recycle bin"""

    __slots__ = ()

    def __init__(self, original_path: str) -> None:
        super().__init__(original_path)

    @override
    def get_undo_message(self) -> str:
        return f"Restore {self.original_path} from trash?"
