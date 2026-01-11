"""
Deals with storing known image file paths and determining their true file extension.
"""

from collections.abc import Iterable

from image_viewer.constants import ImageFormats, Movement
from image_viewer.util.os import os_name_compare


class ImageName:
    """Stores the image file's name and suffix and allows for sorting."""

    __slots__ = ("name", "suffix")

    def __init__(self, name: str) -> None:
        self.name: str = name

        index: int = name.rfind(".") + 1
        self.suffix: str = name[index:].lower() if index else ""

    def __lt__(self, other: "ImageName") -> bool:
        return os_name_compare(self.name, other.name)


class ImageSearchResult:
    """Represents a search such that index is where the image is or would be inserted
    depending on if found is True or False respectively."""

    __slots__ = ("index", "found")

    def __init__(self, index: int, found: bool) -> None:
        self.index: int = index
        self.found = found


class ImageNameList(list[ImageName]):
    """Represents list of ImageName objects with extension methods."""

    __slots__ = ("_display_index",)

    def __init__(self, iterable: Iterable[ImageName]) -> None:
        super().__init__(iterable)
        self._display_index: int = 0

    @property
    def display_index(self) -> int:
        return self._display_index

    def get_current_image(self) -> ImageName:
        """Gets the image at the current.

        :returns: The image at the current index."""

        return self[self._display_index]

    def move_index(self, amount: int) -> None:
        """Moves index by the provided amount with wrap around.

        :param amount: Amount to move the index."""

        image_count: int = len(self)
        if image_count > 0:
            self._display_index = (self._display_index + amount) % len(self)

    def set_index_to_image(self, target_image_name: str) -> None:
        """Sets index to location of target_image_name or where target_image_name would
        be inserted if not present.

        :param target_image_name: The name to search for."""

        search_response: ImageSearchResult = self.search(target_image_name)
        self._display_index = search_response.index

    def sort_and_preserve_index(self, target_image_name: str) -> None:
        """Sorts while keeping index at the same image.

        :param target_image_name: The name to set index to after sorting."""

        super().sort()
        self.set_index_to_image(target_image_name)

    def remove_current_image(self, index_movement: Movement = Movement.NONE) -> None:
        """Safely removes the entry at the current index.

        :param index_movement: The direction to move the index. If NONE passed,
        index will try to preserve its current position."""

        try:
            super().pop(self._display_index)
        except IndexError:
            pass

        image_count: int = len(self)

        # Weird logic here: moving BACKWARD is normal
        # but, if FORWARD then we need to do nothing since
        # keeping index the same and removing an item from the list
        # will effectively move forward. However, if index now exceeds
        # the list size, when NONE we need to wrap back to the end of the list
        # to preserve being at the end of the list. if FORWARD we need to wrap
        # around to index 0
        if index_movement == Movement.BACKWARD:
            self.move_index(-1)
        elif self._display_index >= image_count:
            if index_movement == Movement.NONE:
                self._display_index = image_count - 1
            else:  # Must be Movement.FORWARD
                self._display_index = 0

    def search(self, target_image_name: str) -> ImageSearchResult:
        """Searches for index of target.
        If no match found, index returned is where image would be inserted.

        :param target_image_name: The name to search for.
        :returns: Search result with index and boolean if a match was found or not."""

        low: int = 0
        high: int = len(self) - 1
        while low <= high:
            mid: int = (low + high) >> 1
            current_image = self[mid].name

            if current_image == target_image_name:
                return ImageSearchResult(index=mid, found=True)

            if os_name_compare(target_image_name, current_image):
                high = mid - 1
            else:
                low = mid + 1

        return ImageSearchResult(index=low, found=False)


def magic_number_guess(magic: bytes) -> str:
    """Given a 4 byte long sequence representing an image's magic bytes,
    guess what image it represents. Defaults to AVIF since its the
    only supported image format where the magic is not the first 4 bytes.

    :param magic: The 4 byte long magic number at the start of an image file.
    :returns: The format this magic most likely represents."""

    match magic:
        case b"\x89PNG":
            return ImageFormats.PNG
        case b"RIFF":
            return ImageFormats.WEBP
        case b"GIF8":
            return ImageFormats.GIF
        case b"DDS ":
            return ImageFormats.DDS
        case _:
            return (
                ImageFormats.JPEG if magic[:3] == b"\xff\xd8\xff" else ImageFormats.AVIF
            )
