from unittest.mock import mock_open, patch

import pytest
import tempfile
import os

from image_viewer.constants import ImageFormats
from image_viewer.util.convert import try_convert_file_and_save_new
from tests.test_util.mocks import MockImage
from tests.conftest import IMG_DIR

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
    "image_file_name,target_format",
    [
        ("a.png", ImageFormats.JPEG),
        ("a.png", ImageFormats.WEBP),
        ("a.png", ImageFormats.GIF),
        ("a.png", ImageFormats.DDS),
        ("a.png", ImageFormats.PNG),
        ("a.png", ImageFormats.JPEG),
        ("d.jpg", ImageFormats.PNG),
    ],
)
def test_convert_between_types(image_file_name: str, target_format: str):
    """Should attempt conversion unless image is already target format, ignoring
    the file format in the path and using the format in the files magic bytes"""
    old_path: str = os.path.join(IMG_DIR, image_file_name)

    with tempfile.TemporaryFile() as temp_file:
        converted: bool = try_convert_file_and_save_new(
            old_path, temp_file, target_format, quality=50
        )
        if image_file_name.endswith(target_format.lower()):
            assert not converted
        else:
            assert converted
