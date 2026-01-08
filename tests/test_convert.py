import tempfile
from unittest.mock import mock_open, patch

import pytest

from image_viewer.constants import ImageFormats
from image_viewer.util.convert import try_convert_file_and_save_new
from tests.conftest import EXAMPLE_JPEG_PATH, EXAMPLE_PNG_PATH
from tests.test_util.mocks import MockImage

_MODULE_PATH: str = "image_viewer.util.convert"


def mock_open_image(_: str) -> MockImage:
    return MockImage()


def mock_open_animated_image(_: str) -> MockImage:
    image = MockImage(8)
    return image


def test_animated_to_not_animated():
    with (
        patch(f"{_MODULE_PATH}.open_image", mock_open_animated_image),
        patch(f"{_MODULE_PATH}.magic_number_guess", lambda _: "GIF"),
        patch("builtins.open", mock_open()),
        pytest.raises(ValueError),
    ):
        try_convert_file_and_save_new("asdf.gif", "hjkl.jpg", "jpg")


def test_convert_jpeg():
    with (
        patch(f"{_MODULE_PATH}.open_image", mock_open_image),
        patch("builtins.open", mock_open()),
    ):
        # will not convert if jpeg variant
        with patch(f"{_MODULE_PATH}.magic_number_guess", lambda _: ImageFormats.JPEG):
            assert not try_convert_file_and_save_new("old.jpg", "new.jpe", "jpe")
        # otherwise will succeed
        with patch(f"{_MODULE_PATH}.magic_number_guess", lambda _: ImageFormats.PNG):
            assert try_convert_file_and_save_new("old.png", "new.jpg", "jpg")


def test_convert_to_bad_type():
    """Should return False if an invalid image extension is passed"""
    with (
        patch(f"{_MODULE_PATH}.open_image", mock_open_image),
        patch("image_viewer.image.file.magic_number_guess", lambda _: "JPEG"),
        patch("builtins.open", mock_open()),
    ):
        assert not try_convert_file_and_save_new("old.jpg", "new.txt", "txt")


@pytest.mark.parametrize(
    "image_file_path,target_format",
    [
        (EXAMPLE_PNG_PATH, ImageFormats.JPEG),
        (EXAMPLE_PNG_PATH, ImageFormats.WEBP),
        (EXAMPLE_PNG_PATH, ImageFormats.GIF),
        (EXAMPLE_PNG_PATH, ImageFormats.DDS),
        (EXAMPLE_PNG_PATH, ImageFormats.PNG),
        (EXAMPLE_PNG_PATH, ImageFormats.JPEG),
        (EXAMPLE_JPEG_PATH, ImageFormats.PNG),
    ],
)
def test_convert_between_types(image_file_path: str, target_format: str):
    """Should attempt conversion unless image is already target format, ignoring
    the file format in the path and using the format in the files magic bytes"""

    with tempfile.TemporaryFile() as temp_file:
        converted: bool = try_convert_file_and_save_new(
            image_file_path, temp_file, target_format, quality=50
        )
        if image_file_path.endswith(target_format.lower()):
            assert not converted
        else:
            assert converted
