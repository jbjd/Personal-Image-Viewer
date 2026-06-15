"""Tests for the ZoomState class."""

from image_viewer.constants import ZoomDirection
from image_viewer.image.state import ImageState


def test_try_update_state() -> None:
    """Should move zoom and orientation based on input."""
    state = ImageState()
    state.zoom_level_max = 1

    assert not state.try_update(ZoomDirection.OUT)
    assert state.zoom_level == 0

    assert state.try_update(ZoomDirection.IN)
    assert state.zoom_level == 1

    assert not state.try_update(ZoomDirection.IN)
    assert state.zoom_level == 1

    assert state.try_update(ZoomDirection.OUT)
    assert state.zoom_level == 0


def test_reset() -> None:
    state = ImageState()
    state.zoom_level += 1
    state.zoom_level_max += 2
    state.zoom_allowed = not state.zoom_allowed

    state.reset()

    default_state = ImageState()
    assert state.zoom_level == default_state.zoom_level
    assert state.zoom_level_max == default_state.zoom_level_max
    assert state.zoom_allowed is default_state.zoom_allowed
