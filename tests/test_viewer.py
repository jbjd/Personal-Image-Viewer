"""Tests for the ViewerApp class."""

from unittest.mock import MagicMock, patch

import pytest

from image_viewer.viewer import ViewerApp
from tests.test_util.mocks import MockEvent

_MODULE_PATH: str = "image_viewer.viewer"

# mypy: disable-error-code="method-assign"


def test_pixel_scaling(viewer: ViewerApp):
    """Should correctly scale sizes to the screen."""

    viewer.height_ratio = 1
    viewer.width_ratio = 1
    assert viewer._scale_pixels_to_height(1080) == 1080
    assert viewer._scale_pixels_to_width(1920) == 1920

    viewer.height_ratio = 2.21
    viewer.width_ratio = 1.21
    assert viewer._scale_pixels_to_height(1080) == 2386
    assert viewer._scale_pixels_to_width(1920) == 2323


def test_redraw(
    viewer: ViewerApp, focused_event: MockEvent, unfocused_event: MockEvent
):
    """Should only redraw the current image when necessary."""

    with patch(f"{_MODULE_PATH}.ViewerApp.load_image_unblocking") as mock_refresh:
        with patch(
            f"{_MODULE_PATH}.ImageFileManager.current_image_cache_still_fresh",
            side_effect=lambda: True,
        ):
            viewer.redraw(focused_event)
            mock_refresh.assert_not_called()

        with patch(
            f"{_MODULE_PATH}.ImageFileManager.current_image_cache_still_fresh",
            side_effect=lambda: False,
        ):
            viewer.redraw(unfocused_event)
            mock_refresh.assert_not_called()

        with patch(
            f"{_MODULE_PATH}.ImageFileManager.current_image_cache_still_fresh",
            side_effect=lambda: False,
        ):
            viewer.redraw(focused_event)
            mock_refresh.assert_called_once()


def test_clear_image(viewer: ViewerApp):
    """Should stop animations and reset image loader."""
    mock_after_cancel = MagicMock()
    viewer.app.after_cancel = mock_after_cancel

    viewer.clear_current_image_data()
    mock_after_cancel.assert_not_called()

    viewer.animation_id = "123"

    with patch(f"{_MODULE_PATH}.ImageLoader.reset_and_setup") as mock_reset:
        viewer.clear_current_image_data()
        mock_after_cancel.assert_called_once()
        mock_reset.assert_called_once()


def test_exit(viewer: ViewerApp):
    """Should clean up and exit tkinter."""

    del viewer.canvas

    # Cleans up properly when not fully initialized
    with pytest.raises(SystemExit) as exception_cm:
        viewer.exit(exit_code=1)
    assert exception_cm.value.code == 1

    viewer.canvas = MagicMock()
    viewer.canvas.file_name_text_id = 0
    mock_destroy = MagicMock()
    viewer.app.destroy = mock_destroy

    with pytest.raises(SystemExit) as exception_cm:
        viewer.exit()
    assert exception_cm.value.code == 0
    mock_destroy.assert_called_once()


def test_minimize(viewer: ViewerApp):
    """Should iconify the app and cancel scheduled movements."""

    mock_after_cancel = MagicMock()
    mock_iconify = MagicMock()
    viewer.app.after_cancel = mock_after_cancel
    viewer.app.iconify = mock_iconify

    viewer.minimize()
    assert mock_iconify.call_count == 1
    assert mock_after_cancel.call_count == 0

    viewer.move_id = "12"
    viewer.minimize()
    assert mock_iconify.call_count == 2
    assert mock_after_cancel.call_count == 1


@pytest.mark.parametrize(
    "dropdown_show,dropdown_needs_refresh",
    [
        (False, False),
        (False, True),
        (True, False),
        (True, True),
    ],
)
def test_update_details_dropdown(
    viewer: ViewerApp, dropdown_show: bool, dropdown_needs_refresh: bool
):
    """Should correctly update dropdown given provided state."""
    viewer.canvas.itemconfigure = MagicMock()

    viewer.dropdown.show = dropdown_show
    viewer.dropdown.need_refresh = dropdown_needs_refresh
    with patch(
        "image_viewer.viewer.ImageFileManager.get_cached_metadata", return_value=""
    ):
        viewer.update_details_dropdown()

    if dropdown_show:
        viewer.canvas.itemconfigure.assert_called_once_with(
            viewer.dropdown.id, image=viewer.dropdown.image, state="normal"
        )
        if not dropdown_needs_refresh:
            assert (  # Didn't change
                viewer.dropdown.need_refresh == dropdown_needs_refresh
            )
        else:
            assert not viewer.dropdown.need_refresh

    else:
        viewer.canvas.itemconfigure.assert_called_once_with(
            viewer.dropdown.id, state="hidden"
        )
        assert viewer.dropdown.need_refresh == dropdown_needs_refresh  # Didn't change


@pytest.mark.parametrize("input", (" ", "something.png"))
def test_rename_or_convert(viewer: ViewerApp, input: str):

    event = MagicMock()
    with (
        patch("image_viewer.viewer.RenameEntry.get", return_value=input),
        patch(
            "image_viewer.viewer.ImageFileManager.rename_or_convert_current_image"
        ) as mock_rename_or_convert_current_image,
    ):
        viewer.rename_or_convert(event)

        stripped_input: str = input.strip()
        if stripped_input == "":
            mock_rename_or_convert_current_image.assert_not_called()
        else:
            mock_rename_or_convert_current_image.assert_called_once_with(stripped_input)
