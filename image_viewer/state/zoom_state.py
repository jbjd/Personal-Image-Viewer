"""Classes that represent the zoom state"""

from image_viewer.constants import ZoomDirection
from image_viewer.state.base import StateBase


class ZoomState(StateBase):
    """Represents level of zoom and stores max zoom level"""

    __slots__ = ("level", "max_level")

    def __init__(self) -> None:
        self.level: int = 0
        self.max_level: int = 0

    def reset(self) -> None:
        """Resets zoom level"""
        self.level = 0
        self.max_level = 0

    def try_update_zoom_level(self, direction: ZoomDirection | None) -> bool:
        """Tries to zoom in or out. Returns True if zoom level changed"""
        if direction is None:
            return False

        previous_zoom: int = self.level

        if direction == ZoomDirection.IN and previous_zoom < self.max_level:
            self.level += 1
        elif direction == ZoomDirection.OUT and previous_zoom > 0:
            self.level -= 1

        return previous_zoom != self.level
