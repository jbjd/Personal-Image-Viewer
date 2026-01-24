"""Tests for the ZoomState class."""

from image_viewer.constants import ZoomDirection
from image_viewer.state.zoom_state import ZoomState


def test_try_update_zoom_level():
    """Should move zoom up or down based on input."""
    zoom_state = ZoomState()

    assert zoom_state.level == 0

    updated = zoom_state.try_update_zoom_level(ZoomDirection.OUT)
    assert zoom_state.level == 0
    assert not updated

    updated = zoom_state.try_update_zoom_level(ZoomDirection.IN)
    assert zoom_state.level == 1
    assert updated

    updated = zoom_state.try_update_zoom_level(ZoomDirection.OUT)
    assert zoom_state.level == 0
    assert updated

    zoom_state.reset()

    default_zoom_state = ZoomState()
    assert zoom_state.level == default_zoom_state.level
    assert zoom_state.max_level == default_zoom_state.max_level
