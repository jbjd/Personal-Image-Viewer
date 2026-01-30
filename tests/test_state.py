"""Tests for the ZoomState class."""

from image_viewer.constants import Rotation, ZoomDirection
from image_viewer.image.state import ImageState


def test_try_update_state():
    """Should move zoom and orientation based on input."""
    state = ImageState()
    state.zoom_level_max = 1

    updated = state.try_update(ZoomDirection.OUT, None)
    assert state.zoom_level == 0
    assert not updated

    updated = state.try_update(ZoomDirection.IN, None)
    assert state.zoom_level == 1
    assert updated

    updated = state.try_update(ZoomDirection.IN, None)
    assert state.zoom_level == 1
    assert not updated

    updated = state.try_update(ZoomDirection.OUT, None)
    assert state.zoom_level == 0
    assert updated

    updated = state.try_update(ZoomDirection.IN, Rotation.DOWN)
    assert state.zoom_level == 1
    assert state.orientation == Rotation.DOWN
    assert updated

    updated = state.try_update(None, Rotation.LEFT)
    assert state.orientation == Rotation.LEFT
    assert updated

    updated = state.try_update(None, Rotation.LEFT)
    assert state.orientation == Rotation.LEFT
    assert not updated

    state.zoom_rotate_allowed = False
    state.reset()

    default_state = ImageState()
    assert state.zoom_level == default_state.zoom_level
    assert state.zoom_level_max == default_state.zoom_level_max
    assert state.orientation == default_state.orientation
    assert state.zoom_rotate_allowed is default_state.zoom_rotate_allowed
