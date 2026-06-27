"""Tests for memory leaks in C extension modules."""

import os
import sys

import pytest
from psleak import MemoryLeakTestCase

from compile_utils.exceptions import InvalidEnvironmentError
from image_viewer._config import parse_config_file
from image_viewer.image._read import (
    CRawImageView,
    decode_jpeg_downscaled,
    read_image_into_buffer,
)
from tests.conftest import EXAMPLE_JPEG_PATH, IMG_DIR, ONLY_ON_WINDOWS

if sys.platform == "win32":
    from image_viewer.utils._os_nt import (
        get_files_in_folder,
        read_buffer_as_base64_and_copy_to_clipboard,
    )


@pytest.mark.memory_leak
class TestLeaks(MemoryLeakTestCase):
    warmup_times = 1

    times = 10

    retries = 4

    def setUp(self) -> None:
        self.malloc_env: str | None = os.getenv("PYTHONMALLOC")
        os.environ["PYTHONMALLOC"] = "malloc"

        if os.environ.get("PYTHONUNBUFFERED") != "1":
            raise InvalidEnvironmentError("Need to set env variable PYTHONUNBUFFERED=1")

    def tearDown(self) -> None:
        if self.malloc_env is not None:
            os.environ["PYTHONMALLOC"] = self.malloc_env
        else:
            del os.environ["PYTHONMALLOC"]

    def test_parse_config_file_defaults(self) -> None:
        self.execute(parse_config_file, "some bad path")

    def test_read_image_into_buffer(self) -> None:
        self.execute(read_image_into_buffer, EXAMPLE_JPEG_PATH)

    def test_decode_jpeg_downscaled(self) -> None:
        image_buffer = read_image_into_buffer(EXAMPLE_JPEG_PATH)
        if image_buffer is None:
            raise RuntimeError("Failed to setup test_decode_jpeg_downscaled")

        # Need to call this once before, or psleak gets false flags.
        # I assume this is something with libjpegturbo initialization.
        decode_jpeg_downscaled(image_buffer, 2)

        self.execute(decode_jpeg_downscaled, image_buffer, 2)

    @pytest.mark.skipif(sys.platform != "win32", reason=ONLY_ON_WINDOWS)
    def test_get_files_in_folder(self) -> None:
        self.execute(get_files_in_folder, IMG_DIR)

    @pytest.mark.skipif(sys.platform != "win32", reason=ONLY_ON_WINDOWS)
    def test_read_buffer_as_base64_and_copy_to_clipboard(self) -> None:
        image_view: CRawImageView | None = read_image_into_buffer(EXAMPLE_JPEG_PATH)

        assert image_view is not None

        self.execute(read_buffer_as_base64_and_copy_to_clipboard, image_view)
