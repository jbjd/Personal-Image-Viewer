"""Tests for the ImageLoader class."""

import os
import tempfile
from unittest.mock import MagicMock, mock_open, patch

from PIL import UnidentifiedImageError
from PIL.Image import Image, new

from image_viewer.animation.frame import Frame
from image_viewer.image.cache import ImageCacheEntry
from image_viewer.image.image_io import ImageIO, ReadImageResponse
from tests.conftest import EXAMPLE_JPEG_PATH

_MODULE_PATH: str = "image_viewer.image.io"


def test_next_frame(image_io: ImageIO):
    """Test expected behavior from getting next frame and resetting"""

    frame1, frame2, frame3 = Frame(Image()), Frame(Image()), Frame(Image())
    image_io.animation_frames = [frame1, frame2, frame3]

    example_frame: Frame | None = image_io.get_next_frame()
    assert example_frame is frame2
    example_frame = image_io.get_next_frame()
    assert example_frame is frame3
    example_frame = image_io.get_next_frame()
    assert example_frame is frame1
    example_frame = image_io.get_next_frame()

    # if next is None, should return None but not increment internal frame index
    image_io.animation_frames[2] = None
    example_frame = image_io.get_next_frame()
    assert example_frame is None
    assert image_io.frame_index == 1

    # reset should set all animation variables to defaults
    image_io.reset_and_setup()
    assert len(image_io.animation_frames) == 0
    assert image_io.frame_index == 0

    # program may try to get a frame when the animation frame list is empty
    example_frame = image_io.get_next_frame()
    assert example_frame is None


def test_load_image_error_on_open(image_io: ImageIO):
    """An image might error on open when its not a valid image or not found"""

    with patch("builtins.open", side_effect=FileNotFoundError):
        assert image_io.load_image("") is None

    with (
        patch("builtins.open", mock_open(read_data=b"abcd")),
        patch(f"{_MODULE_PATH}.open_image", side_effect=UnidentifiedImageError()),
    ):
        assert image_io.load_image("") is None


def test_load_image_in_cache(image_io: ImageIO):
    """When an image of the same name is in cache, don't load from disk"""

    # setup cache for test
    image_format: str = "RGB"
    image_byte_size: int = 10
    cached_image = Image()
    cached_data = ImageCacheEntry(
        cached_image, (10, 10), image_byte_size, image_format, "PNG"
    )
    image_io.image_cache["some/path"] = cached_data

    mock_image_buffer = MagicMock()
    mock_image_buffer.byte_size = image_byte_size
    with (
        patch.object(
            ImageIO,
            "read_image",
            lambda *_: ReadImageResponse(mock_image_buffer, Image(), image_format),
        ),
        patch(f"{_MODULE_PATH}.open_image", lambda *_: Image()),
    ):
        assert image_io.load_image("some/path") is cached_image


def test_load_image_resize_error(image_io: ImageIO):
    """Should get placeholder image when resize errors"""
    with (
        patch(
            f"{_MODULE_PATH}.ImageResizer.get_image_fit_to_screen", side_effect=OSError
        ),
        patch(
            f"{_MODULE_PATH}.get_placeholder_for_errored_image"
        ) as mock_get_placeholder,
    ):
        image_io._resize_or_get_placeholder()
        mock_get_placeholder.assert_called_once()

        assert not image_io._state.zoom_rotate_allowed


def test_optimize_png_image_only_pngs(image_io: ImageIO):
    """Should not run on non-PNGs."""

    image_io.load_image(EXAMPLE_JPEG_PATH)

    assert not image_io.optimize_png_image("")


def test_optimize_png_image(image_io: ImageIO):
    """Should saved optimized PNG."""

    original_image = tempfile.NamedTemporaryFile(delete=False)  # noqa: SIM115
    try:
        # Setup uncompressed PNG file
        with original_image:
            image = new("RGBA", (10, 10))
            image.putdata([(i, i + 1, i + 2, 255) for i in range(100)])
            image.save(original_image, "PNG", optimize=False, compress_level=0)

        starting_size: int = os.stat(original_image.name).st_size

        image_io.load_image(original_image.name)
        image_io.optimize_png_image(original_image.name)

        ending_size: int = os.stat(original_image.name).st_size

        assert ending_size > 0
        assert ending_size < starting_size

        # Doing it again does nothing
        with patch(f"{_MODULE_PATH}.optimize_image_mode") as mock_optimize_image_mode:
            assert not image_io.optimize_png_image(original_image.name)
            mock_optimize_image_mode.assert_not_called()

        # Optimizing again should result in nothing happening
        # even if _image_optimized = False
        with patch(f"{_MODULE_PATH}.os.replace") as mock_os_replace:
            image_io._image_optimized = False
            assert not image_io.optimize_png_image(original_image.name)
            mock_os_replace.assert_not_called()
    finally:
        image_io.reset_and_setup()
        original_image.close()
        os.remove(original_image.name)
