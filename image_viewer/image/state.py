"""Classes that represent the zoom state"""

from image_viewer.constants import ZoomDirection

ZOOM_UNSET: int = -1


class ImageState:
    """Represents zoom level of image display."""

    __slots__ = ("zoom_allowed", "zoom_level", "zoom_level_max")

    def __init__(self) -> None:
        self.zoom_level: int = 0
        self.zoom_level_max: int = ZOOM_UNSET
        self.zoom_allowed: bool = True

    def reset(self) -> None:
        """Resets members to default values."""
        ImageState.__init__(self)

    def try_update(self, direction: ZoomDirection) -> bool:
        """Tries to zoom in or out. Returns True if zoom level changed"""
        updated: bool = False

        if direction is not None:
            if direction == ZoomDirection.IN and self.zoom_level < self.zoom_level_max:
                self.zoom_level += 1
                updated = True
            elif direction == ZoomDirection.OUT and self.zoom_level > 0:
                self.zoom_level -= 1
                updated = True

        return updated
