"""Tests for the ButtonIconFactory class."""

import unittest

from PIL.ImageTk import PhotoImage

from image_viewer.ui.button import IconImages
from image_viewer.ui.button_icon_factory import ButtonIconFactory
from tests.setup import setup_tk


class ButtonIconFactoryTests(unittest.TestCase):
    def setUp(self):
        self.button_icon_factory = ButtonIconFactory(32)
        setup_tk()

    def test_create_icons(self):
        """Should successfully create all icons as PhotoImages."""
        topbar: PhotoImage = self.button_icon_factory.make_topbar_image(1920)
        assert isinstance(topbar, PhotoImage)

        _assert_icons(self.button_icon_factory.make_exit_icons())

        _assert_icons(self.button_icon_factory.make_minify_icons())

        _assert_icons(self.button_icon_factory.make_trash_icons())

        _assert_icons(self.button_icon_factory.make_rename_icons())

        down_icons, up_icons = self.button_icon_factory.make_dropdown_icons()

        _assert_icons(down_icons)
        _assert_icons(up_icons)


def _assert_icons(icons: IconImages) -> None:
    """Asserts icons are expected types."""
    assert isinstance(icons.default, PhotoImage)
    assert isinstance(icons.hovered, PhotoImage)

    assert icons.default.width() == 32
    assert icons.default.height() == 32
    assert icons.hovered.width() == 32
    assert icons.hovered.height() == 32
