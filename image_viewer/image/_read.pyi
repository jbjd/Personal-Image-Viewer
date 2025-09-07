"""C extensions that interact with image files."""

class CMemoryViewBuffer:
    """Can't be instantiated in Python.

    Contains a memoryview object to malloc'ed C data."""

    __slots__ = ("byte_size", "view")

    byte_size: int
    view: memoryview

class CMemoryViewBufferJpeg(CMemoryViewBuffer):
    """Can't be instantiated in Python.

    Contains a memoryview object to malloc'ed C data containing a JPEG."""

    __slots__ = ("dimensions",)

    dimensions: tuple[int, int]

def read_image_into_buffer(image_path: str, /) -> CMemoryViewBuffer | None:
    """Reads an image file path and stores it in a buffer.

    :param image_path: A path to a file containing an image.
    :returns: A buffer containing the image data or None on failure."""

def decode_scaled_jpeg(
    image_buffer: CMemoryViewBuffer, scale_factor: tuple[int, int], /
) -> CMemoryViewBufferJpeg:
    """Given an image buffer, decode it as a jpeg and return a new scaled buffer.

    :param image_buffer: An image to decode and scale.
    :param scale_factor: A ratio to scale the image dimensions by.
    :returns: A new buffer containing the scaled and decoded jpeg."""
