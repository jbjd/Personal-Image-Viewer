"""Tests for the actions module."""

from unittest.mock import patch

import pytest

from image_viewer.files.actions import Convert, Delete, FileAction, Rename

_MODULE_PATH = "image_viewer.files.actions"


@pytest.mark.parametrize(
    ("action", "expected_message"),
    [
        (Delete("original_path"), "Restore original_path from trash?"),
        (
            Convert("original_path", "new_path", True),
            "Delete new_path and restore original_path from trash?",
        ),
        (Convert("original_path", "new_path", False), "Delete new_path?"),
        (
            Rename("original_path", "new_path"),
            "Rename new_path back to original_path?",
        ),
    ],
)
def test_undo_action(action: FileAction, expected_message: str) -> None:
    """Should call correct functions based on action to undo"""

    assert action.get_undo_message() == expected_message

    with (
        patch(f"{_MODULE_PATH}.trash_file") as mock_trash,
        patch(f"{_MODULE_PATH}.restore_file") as mock_undelete,
        patch(f"{_MODULE_PATH}.os.rename") as mock_rename,
    ):
        path_restored, path_removed = action.undo()
        _assert_correct_undo_response(action, path_restored, path_removed)

        if type(action) is Delete or (
            type(action) is Convert and action.original_file_deleted
        ):
            mock_undelete.assert_called_once()
        else:
            mock_undelete.assert_not_called()

        if type(action) is Convert:
            mock_trash.assert_called_once()
        else:
            mock_trash.assert_not_called()

        if type(action) is Rename:
            mock_rename.assert_called_once()
        else:
            mock_rename.assert_not_called()


def _assert_correct_undo_response(
    action: FileAction, path_restored: str, path_removed: str
) -> None:
    """Assert that given a specific file actions,
    response has correct values populated."""

    if type(action) is Delete:
        assert not path_removed
    else:
        assert path_removed

    if type(action) is Convert and not action.original_file_deleted:
        assert not path_restored
    else:
        assert path_restored
