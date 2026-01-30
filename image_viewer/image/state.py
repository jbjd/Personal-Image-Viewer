"""Classes that represent the zoom state"""

from image_viewer.constants import Rotation, ZoomDirection

ZOOM_UNSET: int = -1


class ImageState:
    """Represents level of zoom and stores max zoom level"""

    __slots__ = ("orientation", "zoom_level", "zoom_level_max", "zoom_rotate_allowed")

    def __init__(self) -> None:
        self.orientation: Rotation = Rotation.UP
        self.zoom_level: int = 0
        self.zoom_level_max: int = ZOOM_UNSET
        self.zoom_rotate_allowed: bool = True

    def reset(self) -> None:
        """Resets members to default values."""
        self.orientation = Rotation.UP
        self.zoom_level = 0
        self.zoom_level_max = ZOOM_UNSET
        self.zoom_rotate_allowed = True

    def try_update(
        self, direction: ZoomDirection | None, target_orientation: Rotation | None
    ) -> bool:
        """Tries to zoom in or out. Returns True if zoom level changed"""
        updated: bool = False

        if target_orientation is not None and target_orientation != self.orientation:
            self.orientation = target_orientation
            updated = True

        if direction is not None:
            if direction == ZoomDirection.IN and self.zoom_level < self.zoom_level_max:
                self.zoom_level += 1
                updated = True
            elif direction == ZoomDirection.OUT and self.zoom_level > 0:
                self.zoom_level -= 1
                updated = True

        return updated
