"""Common file for pytest framework to define test fixtures, also used to
define other constants used within tests"""

import os
from tkinter import Tk
from unittest.mock import MagicMock, patch

import pytest
from PIL.Image import Image
from PIL.Image import new as new_image
from PIL.ImageTk import PhotoImage

from image_viewer._config import DEFAULT_UI_FONT
from image_viewer.files.file_manager import ImageFileManager
from image_viewer.image.cache import ImageCache
from image_viewer.image.file import ImageName, ImageNameList
from image_viewer.image.image_io import ImageIO
from image_viewer.image.resizer import ImageResizer
from image_viewer.ui.button import IconImages
from image_viewer.ui.button_icon_factory import ButtonIconFactory
from image_viewer.ui.canvas import CustomCanvas
from image_viewer.ui.rename_entry import RenameEntry
from image_viewer.viewer import ViewerApp
from tests.utils.mocks import MockEvent, MockImage

WORKING_DIR: str = os.path.dirname(__file__)
IMG_DIR: str = os.path.join(WORKING_DIR, "example_images")
EXAMPLE_PNG_PATH: str = os.path.join(IMG_DIR, "a.png")
EXAMPLE_WEBP_PATH: str = os.path.join(IMG_DIR, "c.webp")
EXAMPLE_JPEG_PATH: str = os.path.join(IMG_DIR, "d.jpg")
EXAMPLE_DDS_PATH: str = os.path.join(IMG_DIR, "e.dds")
EXAMPLE_AVIF_PATH: str = os.path.join(IMG_DIR, "f.avif")
EXAMPLE_GIF_PATH: str = os.path.join(IMG_DIR, "g.gif")


@pytest.fixture(name="tk", scope="session")
def tk_fixture() -> Tk:
    app = Tk()
    app.withdraw()
    return app


@pytest.fixture(name="canvas")
def canvas_fixture(tk: Tk) -> CustomCanvas:
    custom_canvas = CustomCanvas(tk, "#000000")
    custom_canvas.screen_height = 1080
    custom_canvas.screen_width = 1080
    return custom_canvas


@pytest.fixture(name="button_icon_factory", scope="module")
def button_icon_factory_fixture() -> ButtonIconFactory:
    return ButtonIconFactory(32)


@pytest.fixture(name="image_cache")
def image_cache_fixture() -> ImageCache:
    return ImageCache(20)


@pytest.fixture(name="file_manager")
def file_manager_fixture(image_cache: ImageCache) -> ImageFileManager:
    return ImageFileManager(EXAMPLE_PNG_PATH, image_cache)


@pytest.fixture(name="file_manager_with_3_images")
def file_manager_with_3_images_fixture(image_cache: ImageCache) -> ImageFileManager:
    manager = ImageFileManager(EXAMPLE_PNG_PATH, image_cache)
    manager._files = ImageNameList([*map(ImageName, ("a.png", "c.jpg", "e.webp"))])
    return manager


@pytest.fixture(name="image_resizer")
def image_resizer_fixture() -> ImageResizer:
    return ImageResizer(1920, 1080)


@pytest.fixture(name="image_io")
def image_io_fixture(image_cache: ImageCache) -> ImageIO:
    image_io = ImageIO(1920, 1080, image_cache, lambda *_: None)
    image_io.PIL_image = MockImage()
    return image_io


@pytest.fixture(name="rename_entry")
def rename_entry_fixture(tk: Tk, canvas: CustomCanvas) -> RenameEntry:
    rename_id: int = canvas.create_window(0, 0, width=250, height=20, anchor="nw")
    return RenameEntry(tk, canvas, rename_id, 250, DEFAULT_UI_FONT)


@pytest.fixture(name="viewer")
def viewer_fixture() -> ViewerApp:
    """A Viewer object with visual UI elements mocked out"""

    # This function needs to be unpacked so we must explicitly define it
    mock_icon_factory = MagicMock()
    mock_icon_factory.return_value.make_dropdown_icons.return_value = (
        MagicMock(),
        MagicMock(),
    )

    with (
        patch.object(ViewerApp, "_init_image_display"),
        patch("image_viewer.viewer.Tk"),
        patch("image_viewer.viewer.CustomCanvas"),
        patch("image_viewer.viewer.ButtonIconFactory", mock_icon_factory),
    ):
        return ViewerApp(EXAMPLE_PNG_PATH)


@pytest.fixture(name="focused_event")
def focused_event_fixture(viewer: ViewerApp) -> MockEvent:
    return MockEvent(viewer.app)


@pytest.fixture(name="unfocused_event")
def unfocused_event_fixture() -> MockEvent:
    return MockEvent()


@pytest.fixture(name="example_image", scope="session")
def example_image_fixture() -> Image:
    return new_image("RGB", (10, 10))


@pytest.fixture(name="button_icons", scope="session")
def button_icons_fixture(example_image: Image) -> IconImages:
    default_icon = PhotoImage(example_image)
    hovered_icon = PhotoImage(example_image)
    return IconImages(default_icon, hovered_icon)
