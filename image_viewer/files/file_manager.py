import os
from enum import Enum
from os import stat_result
from time import ctime
from tkinter.messagebox import askyesno

from PIL.Image import Image

from actions.types import Convert, Delete, Rename
from actions.undoer import ActionUndoer, UndoResponse
from constants import VALID_FILE_TYPES, Movement
from files.file_dialog_asker import FileDialogAsker
from image.cache import ImageCache, ImageCacheEntry
from image.file import ImageName, ImageNameList
from util.io import try_convert_file_and_save_new
from util.os import get_files_in_folder, get_normalized_dir_name, trash_file


class _ShouldPreserveIndex(Enum):
    NO = 1
    IF_INSERTED_AT_OR_BEFORE = 2
    YES = 3


class ImageFileManager:
    """Manages interaction with and tracking of image files"""

    __slots__ = (
        "_files",
        "action_undoer",
        "current_image",
        "file_dialog_asker",
        "image_cache",
        "image_folder",
        "path_to_image",
    )

    def __init__(self, first_image_path: str, image_cache: ImageCache) -> None:
        """Load single file for display before we load the rest"""
        self.image_folder: str = get_normalized_dir_name(first_image_path)
        self.image_cache: ImageCache = image_cache

        self.action_undoer: ActionUndoer = ActionUndoer()
        self.file_dialog_asker: FileDialogAsker = FileDialogAsker(VALID_FILE_TYPES)

        first_image_name: ImageName = ImageName(os.path.basename(first_image_path))
        self._files: ImageNameList = ImageNameList([first_image_name])

        self.current_image: ImageName
        self.path_to_image: str
        self._update_after_move_or_edit()

    def validate_current_path(self) -> None:
        """Checks that current path exists and its extension is a valid file type.

        :raises ValueError: If current path is invalid."""

        if (
            not os.path.isfile(self.path_to_image)
            or self.current_image.suffix not in VALID_FILE_TYPES
        ):
            raise ValueError

    def move_to_new_file(self) -> bool:
        """Opens native open file dialog and points to new image if selected.
        Returns True if user selected a file, False if dialog was exited"""
        new_file_path: str = self.file_dialog_asker.ask_open_image(self.image_folder)
        if new_file_path == "":
            return False

        chosen_file: str = os.path.basename(new_file_path)
        new_dir: str = get_normalized_dir_name(new_file_path)

        if new_dir != self.image_folder:
            self.image_folder = new_dir
            self.refresh_files_with_known_starting_image(chosen_file)

        return True

    def get_path_to_image(self, image_name: str) -> str:
        """Given an image file name, returns the full path using the current folder.

        :returns: The full path to the image."""

        return os.path.normpath(f"{self.image_folder}/{image_name}")

    def _update_after_move_or_edit(self) -> None:
        """Sets variables about current image.
        Should be called after adding/deleting an image"""
        self.current_image = self._files.get_current_image()
        self.path_to_image = self.get_path_to_image(self.current_image.name)

    def update_files_with_known_starting_image(
        self, image_to_start_at: str | None = None
    ) -> None:
        """Updates files list with all images in the folder
        and updates the index to where image_to_start_at now is.

        :param image_to_start_at: File name of an image. Starting index will be where
        this falls in the files list. If None, the current image's name will be used.
        """
        if image_to_start_at is None:
            image_to_start_at = self.current_image.name

        self._files = ImageNameList(
            [
                image_name
                for image_name_raw in get_files_in_folder(self.image_folder)
                if (image_name := ImageName(image_name_raw)).suffix in VALID_FILE_TYPES
            ]
        )

        self._files.sort_and_preserve_index(image_to_start_at)
        self._update_after_move_or_edit()

    def refresh_files_with_known_starting_image(
        self, image_to_start_at: str | None = None
    ) -> None:
        """Clears cache, updates files list with all images in the folder,
        and updates the index to where image_to_start_at now is."""
        self.image_cache.clear()
        self.update_files_with_known_starting_image(image_to_start_at)

    def get_cached_metadata(self, get_all_details: bool = True) -> str:
        """Returns formatted string of cached metadata on current image.
        Can raise KeyError on failure to get data."""
        image_info: ImageCacheEntry = self.image_cache[self.path_to_image]
        short_details: str = (
            f"Pixels: {image_info.width}x{image_info.height}\n"
            f"Size: {image_info.size_display}"
        )

        if not get_all_details:
            return short_details

        mode: str = image_info.mode
        bpp: int = len(mode) * 8 if mode != "1" else 1
        readable_mode: str
        match mode:
            case "P":
                readable_mode = "Palette"
            case "L":
                readable_mode = "Grayscale"
            case "1":
                readable_mode = "Black And White"
            case _:
                readable_mode = mode

        details: str = (
            f"{short_details}\n"
            f"Image Format: {image_info.format}\n"
            f"Pixel Format: {bpp} bpp {readable_mode}\n"
        )
        return details

    def get_image_details(
        self, PIL_image: Image  # pylint: disable=invalid-name
    ) -> str | None:
        """Returns a formatted string of data from cache/OS call/PIL object
        or None if failed to read from cache."""
        try:
            details: str = self.get_cached_metadata()
        except KeyError:
            return None  # don't fail trying to read, if not in cache just exit

        try:
            image_metadata: stat_result = os.stat(self.path_to_image)
            created_time_epoch: float = (
                image_metadata.st_birthtime  # type: ignore # Linux
                if os.name == "nt"
                else image_metadata.st_ctime
            )
            modified_time_epoch: float = image_metadata.st_mtime

            # [4:] chops of 3 character day like Mon/Tue/etc.
            created_time: str = ctime(created_time_epoch)[4:]
            modified_time: str = ctime(modified_time_epoch)[4:]
            details += f"Created: {created_time}\nLast Modified: {modified_time}\n"
        except (OSError, ValueError):
            pass  # don't include if can't get

        # Can add more here, just didn't see any others I felt were important enough
        comment_bytes: bytes | None = PIL_image.info.get("comment")
        if comment_bytes is not None:
            # Windows can't show popup window with embedded null byte
            comment: str = comment_bytes.decode("utf-8").replace("\x00", "")
            details += f"Comment: {comment}\n"

        return details

    def move_index(self, amount: int) -> None:
        """Moves index with safe wrap around"""
        self._files.move_index(amount)
        self._update_after_move_or_edit()

    def delete_current_image(self) -> None:
        """Safely deletes the image at the current file path"""
        try:
            trash_file(self.path_to_image)
            self.action_undoer.append(Delete(self.path_to_image))
        except (OSError, FileNotFoundError):
            pass
        self.remove_current_image()

    def remove_current_image(self, index_movement: Movement = Movement.NONE) -> None:
        """Removes current image from files list and cache.

        :param index_movement: The direction to move the index. If NONE passed,
        index will try to preserve its current position."""

        self._files.remove_current_image(index_movement)
        self.image_cache.pop_safe(self.path_to_image)
        self._update_after_move_or_edit()

    def remove_image(self, index: int) -> None:
        """Removes image at index from files list and cache."""
        deleted_name: str = self._files.pop(index).name
        key: str = self.get_path_to_image(deleted_name)
        self.image_cache.pop_safe(key)

    def rename_or_convert_current_image(self, new_name_or_path: str) -> None:
        """Try to either rename or convert based on input"""
        new_dir: str
        new_name: str
        new_dir, new_name = self._split_dir_and_name(new_name_or_path)

        new_image_name: ImageName = ImageName(new_name)
        if new_image_name.suffix not in VALID_FILE_TYPES:
            new_name += f".{self.current_image.suffix}"
            new_image_name = ImageName(new_name)

        original_path: str = self.path_to_image
        new_path: str = self._construct_path_for_rename(new_dir, new_image_name.name)

        # if so, we will need to handle moving forward one index due to how future code
        # removes then adds the image back which will leave one image to the left of
        # the original image after a rename/convert
        was_at_last_index: bool = self._files.display_index == len(self._files) - 1

        result: Rename
        if (
            new_image_name.suffix != self.current_image.suffix
            and try_convert_file_and_save_new(
                original_path, new_path, new_image_name.suffix
            )
        ):
            result = self._ask_to_delete_old_image_after_convert(
                original_path, new_path, new_image_name.suffix
            )
        else:
            result = self._rename(original_path, new_path)
            self._files.remove_current_image()
            self.image_cache.update_key(self.path_to_image, new_path)

        self.action_undoer.append(result)

        # Only add image if its still in the directory we are currently in
        if get_normalized_dir_name(new_path) == get_normalized_dir_name(original_path):
            preserve_index: _ShouldPreserveIndex = (
                _ShouldPreserveIndex.YES
                if was_at_last_index
                else (
                    _ShouldPreserveIndex.IF_INSERTED_AT_OR_BEFORE
                    if self._should_preserve_index_on_rename(result)
                    else _ShouldPreserveIndex.NO
                )
            )

            self.add_new_image(new_name, preserve_index)
        else:
            self._update_after_move_or_edit()

    def _split_dir_and_name(self, new_name_or_path: str) -> tuple[str, str]:
        """Returns tuple with path and file name split up"""
        new_name: str = os.path.basename(new_name_or_path) or self.current_image.name
        new_dir: str = get_normalized_dir_name(new_name_or_path)

        if new_name in (".", ".."):
            # name is actually path specifier
            new_dir = os.path.normpath(os.path.join(new_dir, new_name))
            new_name = self.current_image.name

        return new_dir, new_name

    def _construct_path_for_rename(self, new_dir: str, new_name: str) -> str:
        """Makes new path with validations when moving between directories"""
        will_move_dirs: bool = new_dir != ""

        new_full_path: str
        if will_move_dirs:
            if not os.path.isabs(new_dir):
                new_dir = os.path.normpath(os.path.join(self.image_folder, new_dir))
            if not os.path.exists(new_dir):
                raise OSError
            new_full_path = os.path.join(new_dir, new_name)
        else:
            new_full_path = self.get_path_to_image(new_name)

        if os.path.exists(new_full_path):
            raise FileExistsError

        if will_move_dirs and not askyesno(
            "Confirm move",
            f"Move file to {new_dir} ?",
        ):
            raise OSError

        return new_full_path

    def _ask_to_delete_old_image_after_convert(
        self, original_path: str, new_full_path: str, new_format: str
    ) -> Convert:
        """Asks user to delete old file and returns Convert result"""
        deleted: bool = False

        if askyesno(
            "Confirm deletion",
            f"Converted file to {new_format}, delete old file?",
        ):
            try:
                self.delete_current_image()
            except IndexError:
                pass  # even if no images left, a new one will be added after this
            deleted = True

        return Convert(original_path, new_full_path, deleted)

    def _rename(self, original_path: str, new_path: str) -> Rename:
        """Renames a file and returns the rename result"""
        os.rename(original_path, new_path)
        return Rename(original_path, new_path)

    @staticmethod
    def _should_preserve_index_on_rename(result: Rename) -> bool:
        """Returns True when image list shifted or changed size so index
        needs to be changed to keep on the same image"""
        if isinstance(result, Convert):
            return not result.original_file_deleted

        return False

    def add_new_image(
        self,
        new_name: str,
        preserve_index: _ShouldPreserveIndex = _ShouldPreserveIndex.NO,
        index: int = -1,
    ) -> None:
        """Adds a new image to the image list
        preserve_index: try to keep index at the same image it was before adding
        index: where the image is inserted if provided"""
        image_name: ImageName = ImageName(new_name)
        if index < 0:
            index, _ = self._files.get_index_of_image(image_name.name)

        self._files.insert(index, image_name)
        if preserve_index == _ShouldPreserveIndex.YES or (
            preserve_index == _ShouldPreserveIndex.IF_INSERTED_AT_OR_BEFORE
            and index <= self._files.display_index
        ):
            self._files.move_index(1)

        self._update_after_move_or_edit()

    def undo_most_recent_action(self) -> bool:
        """Attempts to undo most recent action after confirming with user.

        :returns: True if most recent action was undone."""
        if not self._confirm_undo():
            return False

        try:
            undo_response: UndoResponse = self.action_undoer.undo()
        except OSError:
            return False  # TODO: error popup?

        image_to_add: str = os.path.basename(undo_response.path_to_restore)
        image_to_remove: str = os.path.basename(undo_response.path_to_remove)

        if image_to_remove != "":
            index: int
            found: bool
            index, found = self._files.get_index_of_image(image_to_remove)
            if found:
                self.remove_image(index)

        if image_to_add != "":
            preserve_index: _ShouldPreserveIndex = (
                _ShouldPreserveIndex.IF_INSERTED_AT_OR_BEFORE
                if image_to_remove == ""
                else _ShouldPreserveIndex.NO
            )
            self.add_new_image(image_to_add, preserve_index)
        else:
            self._update_after_move_or_edit()

        return True

    def _confirm_undo(self) -> bool:
        """Checks that there is an action to undo and shows a yes/no confirmation popup.

        :returns: True if theres something to undo and user said yes"""
        undo_message: str | None = self.action_undoer.get_undo_message()

        return False if undo_message is None else askyesno("Undo Action", undo_message)

    def current_image_cache_still_fresh(self) -> bool:
        """Checks if cache for currently displayed image is still up to date"""
        return self.image_cache.image_cache_still_fresh(self.path_to_image)
