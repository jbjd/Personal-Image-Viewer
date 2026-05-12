import pytest

from image_viewer.constants import ImageFormats
from image_viewer.utils.convert import try_convert_image_and_save_new
from tests.utils.mocks import MockImage


def test_animated_to_not_animated():
    """Should raise ValueError when converted animated image to a unsupported format."""
    with pytest.raises(ValueError):
        try_convert_image_and_save_new(
            MockImage(n_frames=3, image_format="GIF"), "hjkl.jpg", "jpg"
        )


def test_jpeg_to_jpeg_variant():
    """Should return False when converting between jpeg variants like jpg and jpe."""
    assert not try_convert_image_and_save_new(
        MockImage(image_format="JPEG"), "new.jpe", "jpe"
    )


def test_convert_to_bad_type():
    """Should return False if an invalid image extension is passed."""
    assert not try_convert_image_and_save_new(
        MockImage(image_format="PNG"), "new.txt", "txt"
    )

    assert not try_convert_image_and_save_new(MockImage(), "new.png", "png")


@pytest.mark.parametrize(
    ("true_file_extension", "target_format"),
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

    converted: bool = try_convert_image_and_save_new(
        MockImage(image_format=true_file_extension.upper()), "new.jpg", target_format
    )
    assert converted is (true_file_extension != target_format)
