"""Classes that represent the rotation state"""

from image_viewer.constants import Rotation
from image_viewer.state.base import StateBase


class RotationState(StateBase):
    """Represents current rotation orientation of the image"""

    __slots__ = ("orientation",)

    def __init__(self) -> None:
        self.orientation: Rotation = Rotation.UP

    def reset(self) -> None:
        """Resets orientation to default"""
        self.orientation = Rotation.UP

    def try_update_state(self, target_orientation: Rotation | None) -> bool:
        """Tries to update orientation. Returns True if orientation changed"""
        if target_orientation is None or target_orientation == self.orientation:
            return False

        self.orientation = target_orientation
        return True
