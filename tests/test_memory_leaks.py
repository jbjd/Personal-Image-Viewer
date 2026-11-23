"""Tests for memory leaks in C extension modules."""

import sys

from personal_testing_tools.mark import mark_windows_only
from personal_testing_tools.psleak import MemoryLeakTestCaseExt

from image_viewer._config import parse_config_file
from image_viewer.image._read import (
    CRawImageView,
    decode_jpeg_downscaled,
    read_image_into_buffer,
)
from tests.conftest import EXAMPLE_JPEG_PATH, IMG_DIR

if sys.platform == "win32":
    from image_viewer.utils._os_nt import (
        get_files_in_folder,
        read_buffer_as_base64_and_copy_to_clipboard,
    )
else:
    # mypy
    get_files_in_folder = lambda _: ""
    read_buffer_as_base64_and_copy_to_clipboard = lambda _: None


class TestLeaks(MemoryLeakTestCaseExt):  # noqa: D101
    warmup_times = 2

    times = 20

    retries = 4

    def test_parse_config_file_defaults(self):
        self.execute(parse_config_file, "some bad path")

    def test_validate_config_file(self):
        self.execute(parse_config_file, "image_viewer/config.ini")

    def test_read_image_into_buffer(self):
        self.execute(read_image_into_buffer, EXAMPLE_JPEG_PATH)

    def test_decode_jpeg_downscaled(self):
        image_buffer = read_image_into_buffer(EXAMPLE_JPEG_PATH)
        if image_buffer is None:
            raise RuntimeError("Failed to setup test_decode_jpeg_downscaled")

        # Need to call this once before, or psleak gets false flags.
        # I assume this is something with libjpegturbo initialization.
        decode_jpeg_downscaled(image_buffer, 2)

        self.execute(decode_jpeg_downscaled, image_buffer, 2)

    @mark_windows_only()
    def test_get_files_in_folder(self):
        self.execute(get_files_in_folder, IMG_DIR)

    @mark_windows_only()
    def test_read_buffer_as_base64_and_copy_to_clipboard(self):
        image_view: CRawImageView | None = read_image_into_buffer(EXAMPLE_JPEG_PATH)

        assert image_view is not None

        self.execute(read_buffer_as_base64_and_copy_to_clipboard, image_view)
