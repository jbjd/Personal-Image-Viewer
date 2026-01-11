"""
Classes that handle undoing things a user did
"""

import os
from collections import deque
from typing import assert_never

from image_viewer.actions.types import Convert, Delete, FileAction, Rename
from image_viewer.util.os import restore_file, trash_file


class UndoResponse:
    """Contains what paths where restored or removed, if any,
    when an action was undone."""

    __slots__ = ("path_removed", "path_restored")

    def __init__(self, path_restored: str, path_removed: str) -> None:
        self.path_restored: str = path_restored
        self.path_removed: str = path_removed


class ActionUndoer(deque[FileAction]):
    """Keeps track of recent file actions and can undo them."""

    __slots__ = ()

    def __init__(self, max_length: int = 8) -> None:
        super().__init__(maxlen=max_length)

    def undo(self) -> UndoResponse:
        """Undoes most recent action. Files will be renamed, trashed, and or restored
        from trash to match the expected file state before the action occurred.

        :returns: An UndoResponse with the restored/removed file paths if any."""

        action: FileAction = self.pop()

        if type(action) is Rename:
            os.rename(action.new_path, action.original_path)
            return UndoResponse(action.original_path, action.new_path)

        if type(action) is Convert and action.original_file_deleted:
            restore_file(action.original_path)
            trash_file(action.new_path)
            return UndoResponse(action.original_path, action.new_path)

        if type(action) is Convert:
            trash_file(action.new_path)
            return UndoResponse("", action.new_path)

        if type(action) is Delete:
            restore_file(action.original_path)
            return UndoResponse(action.original_path, "")

        assert_never(  # pragma: no cover
            action.__class__.__name__  # type: ignore
        )

    def get_undo_message(self) -> str | None:
        """Returns a friendly message about what the undo action will do.

        :returns: A friendly message or None if self is empty."""

        if not self:
            return None

        action: FileAction = self[-1]

        if type(action) is Rename:
            return f"Rename {action.new_path} back to {action.original_path}?"
        if type(action) is Convert and action.original_file_deleted:
            return (
                f"Delete {action.new_path} and restore {action.original_path}"
                " from trash?"
            )
        if type(action) is Convert:
            return f"Delete {action.new_path}?"
        if type(action) is Delete:
            return f"Restore {action.original_path} from trash?"

        assert_never(  # pragma: no cover
            action.__class__.__name__  # type: ignore
        )
