"""C extensions that interact with image files."""

PNG: str = "PNG"
JPEG: str = "JPEG"
GIF: str = "GIF"
WEBP: str = "WEBP"
AVIF: str = "AVIF"
DDS: str = "DDS"

class CRawImageView:
    """Can't be instantiated in Python.

    Contains a memoryview object to malloc'ed C data."""

    __slots__ = ("format", "view")

    format: str
    view: memoryview

class CDecodedJpegView:
    """Can't be instantiated in Python.

    Contains a memoryview object to malloc'ed C data containing a JPEG."""

    __slots__ = ("dimensions", "view")

    dimensions: tuple[int, int]
    view: memoryview

def read_image_into_buffer(image_path: str, /) -> CRawImageView | None:
    """Reads an image file path and stores it in a buffer.

    :param image_path: A path to a file containing an image
    :returns: A buffer containing the image data or None on failure"""

def decode_jpeg_downscaled(
    image_view: CRawImageView, scale_factor: int, /
) -> CDecodedJpegView:
    """Decodes an image buffer as a jpeg and returns a new downscaled buffer.

    :param image_view: View to a buffer
    :param scale_factor: Factor to downscale by
    :returns: A new view to a buffer containing the decoded and downscaled jpeg"""
