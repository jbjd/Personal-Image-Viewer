"""C extensions that interact with the Windows API."""

import sys

from image_viewer.image._read import CMemoryViewBuffer

if sys.platform != "win32":
    def read_buffer_as_base64(image_buffer: CMemoryViewBuffer, /) -> str:
        """Given an image buffer, converts it to base64.

        :param image_buffer: The image buffer to convert
        :returns: Buffer as base64"""
