"""Tests for memory leaks in C extension modules."""

from psleak import MemoryLeakTestCase, UnclosedHandleError

from image_viewer.image._read import read_image_into_buffer, decode_scaled_jpeg
from tests.conftest import EXAMPLE_JPEG_PATH


class TestLeaks(MemoryLeakTestCase):
    def test_read_image_into_buffer(self):
        self.execute(read_image_into_buffer, EXAMPLE_JPEG_PATH)

    def test_decode_scaled_jpeg(self):
        image_buffer = read_image_into_buffer(EXAMPLE_JPEG_PATH)
        if image_buffer is None:
            raise RuntimeError("Failed to setup test_decode_scaled_jpeg")

        self.execute(decode_scaled_jpeg, image_buffer, (1, 2))
