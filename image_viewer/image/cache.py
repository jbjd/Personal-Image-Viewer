"""Caching image data."""

from collections import OrderedDict
from os import stat

from PIL.Image import Image


class ImageCacheEntry:
    """Cached image data to skip resizing/system calls on repeated opening."""

    __slots__ = (
        "format",
        "height",
        "image",
        "mode",
        "size_display",
        "byte_size",
        "width",
    )

    def __init__(
        self,
        image: Image,
        dimensions: tuple[int, int],
        size_display: str,
        byte_size: int,
        mode: str,
        format: str,
    ) -> None:
        self.width: int
        self.height: int
        self.width, self.height = dimensions
        self.image: Image = image
        self.size_display: str = size_display
        self.byte_size: int = byte_size
        # Store original mode since resizing some images converts to RGB
        self.mode: str = mode
        self.format: str = format


class ImageCache(OrderedDict[str, ImageCacheEntry]):
    """Dictionary for caching image data using paths as keys"""

    __slots__ = ("max_items_in_cache",)

    def __init__(self, max_items_in_cache: int) -> None:
        super().__init__()
        self.max_items_in_cache: int = max_items_in_cache

    def pop_safe(self, image_path: str) -> ImageCacheEntry | None:
        """Pops image_path key and returns its value or None if it doesn't exist.

        :param image_path: The key to pop.
        :returns: The cache entry or None if it doesn't exist."""

        return self.pop(image_path, None)

    def image_cache_still_fresh(self, image_path: str) -> bool:
        """Checks if the file at image_path matches the size of the cached image.
        This heuristic will have false-positives but that is acceptable for this case.

        :param image_path: The key to check.
        :returns: True if the file exists, is in the dictionary,
            and matches file size on disk."""

        cache_entry: ImageCacheEntry | None = self.get(image_path, None)

        if cache_entry is None:
            return False

        try:
            return stat(image_path).st_size == cache_entry.byte_size
        except (FileNotFoundError, OSError):
            return False

    def update_key(self, old_image_path: str, new_image_path: str) -> None:
        """Moves value from old_image_path to new_image_path.
        If old_image_path doesn't exist, does nothing.

        :param old_image_path: The key to be moved.
        :param new_image_path: The key to move to."""

        target: ImageCacheEntry | None = self.pop_safe(old_image_path)

        if target is not None:
            self[new_image_path] = target

    def __setitem__(self, key: str, value: ImageCacheEntry) -> None:
        """Adds check for size of the cache and purges
        least recently used (LRU) if over the limit."""

        if self.max_items_in_cache <= 0:
            return

        if self.__len__() >= self.max_items_in_cache:
            self.popitem(last=False)

        super().__setitem__(key, value)
