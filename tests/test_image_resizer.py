from unittest.mock import MagicMock, patch

import pytest
from PIL.Image import Image, Resampling
from PIL.Image import new as new_image

from image_viewer.image._read import JPEG
from image_viewer.image.image_io import ImageIO, ReadImageResponse
from image_viewer.image.resizer import ImageResizer
from image_viewer.utils.PIL import resize
from tests.conftest import IMG_DIR


def test_jpeg_scale_factor(image_resizer: ImageResizer) -> None:
    """Should return correct ratios for a 1080x1920 screen"""
    assert image_resizer._get_jpeg_fit_to_screen_downscale_factor(9999, 9999) == 8
    assert image_resizer._get_jpeg_fit_to_screen_downscale_factor(6666, 6666) == 4
    assert image_resizer._get_jpeg_fit_to_screen_downscale_factor(3000, 3000) == 2
    assert image_resizer._get_jpeg_fit_to_screen_downscale_factor(1, 1) == 1


@pytest.mark.parametrize(
    ("dimensions", "expected_dimensions"),
    [
        ((600, 800), (810, 1080)),
        ((2000, 800), (1920, 768)),
        ((2000, 2000), (1080, 1080)),
    ],
)
def test_fit_dimensions_to_screen_and_get_interpolation(
    image_resizer: ImageResizer,
    dimensions: tuple[int, int],
    expected_dimensions: tuple[int, int],
) -> None:
    """Should return correct dimensions and interpolation for a 1920x1080 screen"""
    width, height = dimensions
    fit_dimensions = image_resizer.fit_dimensions_to_screen(width, height)
    assert fit_dimensions == expected_dimensions


def test_jpeg_fit_to_screen_small_image(image_resizer: ImageResizer) -> None:
    """When fitting a small jpeg, should fallback to generic fit function"""
    image: Image = new_image("RGB", (1000, 1000))  # smaller than screen

    view = MagicMock()
    view.format = JPEG

    with (
        patch.object(
            ImageResizer,
            "_get_jpeg_fit_to_screen",
            wraps=image_resizer._get_jpeg_fit_to_screen,
        ) as wrapped_get_jpeg_fit_to_screen,
        patch.object(
            ImageResizer,
            "_get_jpeg_downscaled",
            wraps=image_resizer._get_jpeg_downscaled,
        ) as wrapped_get_jpeg_downscaled,
    ):
        _: Image = image_resizer.get_image_fit_to_screen(image, view)
        wrapped_get_jpeg_fit_to_screen.assert_called_once()
        wrapped_get_jpeg_downscaled.assert_not_called()


def test_jpeg_fit_to_screen_large_image(
    image_io: ImageIO, image_resizer: ImageResizer
) -> None:
    """When fitting a large jpeg, should call turbojpeg and scale it down"""

    image: Image = new_image("RGB", (1000, 4000))

    read_image_response: ReadImageResponse | None = image_io.read_image(
        IMG_DIR + "/sub_folder.png/large.jpg"
    )

    assert read_image_response is not None

    with patch.object(
        ImageResizer, "_get_jpeg_downscaled", wraps=image_resizer._get_jpeg_downscaled
    ) as wrapped_get_jpeg_downscaled:
        resized_image: Image = image_resizer.get_image_fit_to_screen(
            image, read_image_response.image_view
        )
        wrapped_get_jpeg_downscaled.assert_called_once()

    # Scaled based on 1920x1080 screen
    assert resized_image.width == 270
    assert resized_image.height == 1080


@pytest.mark.parametrize(
    ("image", "expected_resampling"),
    [
        (new_image("P", (10, 10)), Resampling.LANCZOS),
        (new_image("RGBA", (3000, 3000)), Resampling.HAMMING),
    ],
)
def test_get_image_fit_to_screen(
    image_resizer: ImageResizer, image: Image, expected_resampling: Resampling
) -> None:
    """Should resize and return PIL image"""

    view = MagicMock()
    view.format = "asdf"

    with (
        patch("image_viewer.image.resizer.resize", wraps=resize) as wrapped_resize,
        patch.object(
            ImageResizer, "_get_jpeg_fit_to_screen"
        ) as mock_get_jpeg_fit_to_screen,
    ):
        resized_image: Image = image_resizer.get_image_fit_to_screen(image, view)
        wrapped_resize.assert_called_once_with(image, (1080, 1080), expected_resampling)
        mock_get_jpeg_fit_to_screen.assert_not_called()

    assert resized_image.mode == image.mode
