"""Classes for resizing PIL images"""

from PIL.Image import Image, Resampling, frombytes

from image_viewer.image._read import (
    JPEG,
    CDecodedJpegView,
    CRawImageView,
    decode_jpeg_downscaled,
)
from image_viewer.utils.PIL import resize

JPEG_MAX_DIMENSION: int = 65_535


class ImageResizer:
    """Handles resizing images to fit to the screen"""

    __slots__ = ("jpeg_helper", "screen_height", "screen_width")

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height

    def get_image_zoomed_to(
        self, image: Image, new_width: int, new_height: int, snap_if_small: bool
    ) -> Image | None:
        """Resizes image to provided dimensions.

        :param new_width: To resize to
        :param new_height: To resize to
        :param snap_if_small: Snaps dimensions to screen edges if not already
        :returns: Resized Image or None if dimensions too large"""

        if self._too_big(new_width, new_height):
            return None

        if snap_if_small and (
            new_height < self.screen_height or new_width < self.screen_width
        ):
            maybe_width: int
            maybe_height: int
            maybe_width, maybe_height = (
                self._fit_dimensions_to_screen_height(new_width, new_height)
                if new_height < self.screen_height
                else self._fit_dimensions_to_screen_width(new_width, new_height)
            )
            if not self._too_big(maybe_width, maybe_height):
                new_width = maybe_width
                new_height = maybe_height

        resampling: Resampling = (
            Resampling.HAMMING if new_width < image.width else Resampling.BILINEAR
        )

        return resize(image, (new_width, new_height), resampling)

    def _too_big(self, width: int, height: int) -> bool:
        """Returns if dimenons are too big and Resizer will not accept them."""
        return width > JPEG_MAX_DIMENSION or height > JPEG_MAX_DIMENSION

    def get_image_fit_to_screen(self, image: Image, image_view: CRawImageView) -> Image:
        """Resizes image to screen with PIL"""
        if image_view.format == JPEG:
            return self._get_jpeg_fit_to_screen(image, image_view)

        return self._get_generic_fit_to_screen(image)

    def _get_jpeg_fit_to_screen(self, image: Image, image_view: CRawImageView) -> Image:
        """Resizes a JPEG utilizing libjpeg-turbo to shrink very large images"""
        image_width, image_height = image.size
        scale_factor: int = self._get_jpeg_fit_to_screen_downscale_factor(
            image_width, image_height
        )

        # if small do a normal resize, otherwise utilize libJpegTurbo
        if scale_factor < 2:
            return self._get_generic_fit_to_screen(image)

        return self._get_generic_fit_to_screen(
            self._get_jpeg_downscaled(image_view, scale_factor)
        )

    def _get_jpeg_fit_to_screen_downscale_factor(
        self, image_width: int, image_height: int
    ) -> int:
        """Gets power of 2 downscaling for libturbojpeg to best fit it to the screen.

        :param image_width: Width of image
        :param image_height: Height of image
        :returns: A power of 2 (minimum 1) downscale to use"""

        width_ratio: float = image_width / self.screen_width
        height_ratio: float = image_height / self.screen_height
        ratio_to_screen: int = int(
            width_ratio if width_ratio > height_ratio else height_ratio
        )

        # Gets nearest power of 2 of ratio_to_screen rounded down
        return (
            1 if ratio_to_screen <= 1 else 1 << (int(ratio_to_screen).bit_length() - 1)
        )

    def _get_generic_fit_to_screen(self, image: Image) -> Image:
        image_width, image_height = image.size
        dimensions: tuple[int, int] = self.fit_dimensions_to_screen(
            image_width, image_height
        )

        resampling: Resampling = (
            Resampling.HAMMING if dimensions[0] < image_width else Resampling.LANCZOS
        )

        return resize(image, dimensions, resampling)

    def _get_jpeg_downscaled(
        self, image_view: CRawImageView, scale_factor: int
    ) -> Image:
        jpeg_result: CDecodedJpegView = decode_jpeg_downscaled(image_view, scale_factor)
        # TODO: Remove ignore after https://github.com/python-pillow/Pillow/pull/9410
        return frombytes("RGB", jpeg_result.dimensions, jpeg_result.view)  # type: ignore[arg-type]

    def fit_dimensions_to_screen(
        self, image_width: int, image_height: int
    ) -> tuple[int, int]:
        """Fits dimensions to height if width within screen,
        else fit to width and let height go off screen.
        Returns new width/height to use"""
        fit_to_height: tuple[int, int] = self._fit_dimensions_to_screen_height(
            image_width, image_height
        )
        return (
            fit_to_height
            if fit_to_height[0] <= self.screen_width
            else self._fit_dimensions_to_screen_width(image_width, image_height)
        )

    def _fit_dimensions_to_screen_height(
        self, image_width: int, image_height: int
    ) -> tuple[int, int]:
        """Fits dimensions to screen's height"""
        width: int = round(image_width * (self.screen_height / image_height))
        return (width, self.screen_height)

    def _fit_dimensions_to_screen_width(
        self, image_width: int, image_height: int
    ) -> tuple[int, int]:
        """Fits dimensions to screen's width"""
        height: int = round(image_height * (self.screen_width / image_width))
        return (self.screen_width, height)
