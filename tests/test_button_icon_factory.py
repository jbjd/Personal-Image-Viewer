"""Tests for the ButtonIconFactory class."""

from tkinter import Tk

from PIL.ImageTk import PhotoImage

from image_viewer.ui.button import IconImages
from image_viewer.ui.button_icon_factory import ButtonIconFactory


def test_create_icons(
    # unused tk_app needed to create photo images
    tk_app: Tk,  # noqa: ARG001
    button_icon_factory: ButtonIconFactory,
):
    """Should successfully create all icons as PhotoImages."""
    topbar: PhotoImage = button_icon_factory.make_topbar_image(1920)
    assert isinstance(topbar, PhotoImage)

    _assert_icons_type(button_icon_factory.make_exit_icons())

    _assert_icons_type(button_icon_factory.make_minify_icons())

    _assert_icons_type(button_icon_factory.make_trash_icons())

    _assert_icons_type(button_icon_factory.make_rename_icons())

    down_icons, up_icons = button_icon_factory.make_dropdown_icons()

    _assert_icons_type(down_icons)
    _assert_icons_type(up_icons)


def _assert_icons_type(icons: IconImages) -> None:
    """Asserts icons are expected types."""
    assert isinstance(icons.default, PhotoImage)
    assert isinstance(icons.hovered, PhotoImage)
