"""Tests for memory leaks in C extension modules."""

import os

from psleak import MemoryLeakTestCase
import pytest

from image_viewer.image._read import decode_scaled_jpeg, read_image_into_buffer
from tests.conftest import EXAMPLE_JPEG_PATH


@pytest.mark.memory_leak
class TestLeaks(MemoryLeakTestCase):

    warmup_times = 1

    times = 10

    retries = 4

    def setUp(self) -> None:
        self.malloc_env: str | None = os.getenv("PYTHONMALLOC")
        os.environ["PYTHONMALLOC"] = "malloc"

        if os.environ.get("PYTHONUNBUFFERED") != "1":
            raise EnvironmentError("Need to set env variable PYTHONUNBUFFERED=1")

    def tearDown(self) -> None:
        if self.malloc_env is not None:
            os.environ["PYTHONMALLOC"] = self.malloc_env
        else:
            del os.environ["PYTHONMALLOC"]

    def test_read_image_into_buffer(self):
        self.execute(read_image_into_buffer, EXAMPLE_JPEG_PATH)

    def test_decode_scaled_jpeg(self):
        image_buffer = read_image_into_buffer(EXAMPLE_JPEG_PATH)
        if image_buffer is None:
            raise RuntimeError("Failed to setup test_decode_scaled_jpeg")

        # Need to call this once before, or psleak gets false flags.
        # I assume this is something with libjpegturbo initialization.
        decode_scaled_jpeg(image_buffer, (1, 2))

        self.execute(decode_scaled_jpeg, image_buffer, (1, 2))
