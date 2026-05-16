"""Tests for the ZoomState class."""

from image_viewer.constants import Rotation, ZoomDirection
from image_viewer.image.state import ImageState


def test_try_update_state() -> None:
    """Should move zoom and orientation based on input."""
    state = ImageState()
    state.zoom_level_max = 1

    assert not state.try_update(ZoomDirection.OUT, None)
    assert state.zoom_level == 0

    assert state.try_update(ZoomDirection.IN, Rotation.DOWN)
    assert state.zoom_level == 1
    assert state.orientation == Rotation.DOWN

    assert not state.try_update(ZoomDirection.IN, None)
    assert state.zoom_level == 1

    assert state.try_update(ZoomDirection.OUT, None)
    assert state.zoom_level == 0

    # Mypy bug? 'Literal[Rotation.DOWN]' non-overlaps 'Literal[Rotation.LEFT]'
    assert state.try_update(None, Rotation.LEFT)
    assert state.orientation == Rotation.LEFT  # type: ignore[comparison-overlap]

    assert not state.try_update(ZoomDirection.OUT, Rotation.LEFT)
    assert state.orientation == Rotation.LEFT


def test_reset() -> None:
    state = ImageState()
    state.zoom_level += 1
    state.zoom_level_max += 2
    state.orientation = Rotation.RIGHT
    state.zoom_rotate_allowed = not state.zoom_rotate_allowed

    state.reset()

    default_state = ImageState()
    assert state.zoom_level == default_state.zoom_level
    assert state.zoom_level_max == default_state.zoom_level_max
    assert state.orientation == default_state.orientation
    assert state.zoom_rotate_allowed is default_state.zoom_rotate_allowed
