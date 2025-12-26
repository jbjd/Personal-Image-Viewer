from unittest.mock import patch

import pytest

from image_viewer.constants import ImageFormats
from image_viewer.util.convert import try_convert_file_and_save_new
from tests.test_util.mocks import MockImage

_MODULE_PATH: str = "image_viewer.util.convert"


def mock_open_image(_: str) -> MockImage:
    return MockImage()


def mock_open_animated_image(_: str) -> MockImage:
    image = MockImage(n_frames=8)
    return image


def test_animated_to_not_animated():
    """Should raise ValueError when converted animated image to a unsupported format."""
    with (
        patch(f"{_MODULE_PATH}.open_image", mock_open_animated_image),
        pytest.raises(ValueError),
    ):
        try_convert_file_and_save_new("asdf.gif", "hjkl.jpg", "GIF", "jpg")


def test_jpeg_to_jpeg_variant():
    """Should return False when converting between jpeg variants like jpg and jpe."""
    with patch(f"{_MODULE_PATH}.open_image", mock_open_image):
        assert not try_convert_file_and_save_new("old.jpg", "new.jpe", "jpg", "jpe")


@pytest.mark.parametrize(
    "true_file_extension,target_format",
    [
        (ImageFormats.WEBP, ImageFormats.PNG),
        (ImageFormats.PNG, ImageFormats.JPEG),
        (ImageFormats.PNG, ImageFormats.WEBP),
        (ImageFormats.PNG, ImageFormats.GIF),
        (ImageFormats.PNG, ImageFormats.DDS),
        (ImageFormats.PNG, ImageFormats.PNG),
        (ImageFormats.JPEG, ImageFormats.JPEG),
    ],
)
def test_convert_between_types(true_file_extension: str, target_format: str):
    """Should attempt conversion unless image is already target format, ignoring
    the file format in the path and using the format in the files magic bytes"""
    with patch(f"{_MODULE_PATH}.open_image", mock_open_image):
        converted: bool = try_convert_file_and_save_new(
            "old.png", "new.jpg", true_file_extension, target_format
        )
        assert converted is (true_file_extension != target_format)


def test_convert_to_bad_type():
    """Should return False if an invalid image extension is passed."""
    with patch(f"{_MODULE_PATH}.open_image", mock_open_image):
        assert not try_convert_file_and_save_new("old.jpg", "new.txt", "PNG", "txt")
