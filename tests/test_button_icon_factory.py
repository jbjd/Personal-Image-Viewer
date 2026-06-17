"""Tests for the ButtonIconFactory class."""

from tkinter import Tk

from PIL.ImageTk import PhotoImage

from image_viewer.ui.button import IconImages
from image_viewer.ui.button_icon_factory import DEFAULT_ICON_SIZE, ButtonIconFactory


def test_create_icons(
    tk: Tk,  # noqa: ARG001
    button_icon_factory: ButtonIconFactory,
) -> None:
    """Should successfully create all icons as PhotoImages."""
    topbar: PhotoImage = button_icon_factory.make_topbar_image(1920)
    assert isinstance(topbar, PhotoImage)
    assert topbar.width() == 1920
    assert topbar.height() == 32

    _assert_icons(button_icon_factory.make_exit_icons())

    _assert_icons(button_icon_factory.make_minify_icons())

    _assert_icons(button_icon_factory.make_trash_icons())

    _assert_icons(button_icon_factory.make_rename_icons())

    down_icons, up_icons = button_icon_factory.make_dropdown_icons()

    _assert_icons(down_icons)
    _assert_icons(up_icons)


def _assert_icons(icons: IconImages) -> None:
    """Asserts icons are expected types."""
    _assert_icon(icons.default)
    _assert_icon(icons.hovered)


def _assert_icon(icon: PhotoImage) -> None:
    assert isinstance(icon, PhotoImage)
    assert (icon.width(), icon.height()) == DEFAULT_ICON_SIZE
