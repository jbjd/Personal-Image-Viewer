import sys

import pytest

from tests.conftest import EXAMPLE_WEBP_PATH, ONLY_ON_WINDOWS

if sys.platform == "win32":
    from image_viewer.image._read import read_image_into_buffer
    from image_viewer.utils._os_nt import read_buffer_as_base64_and_copy_to_clipboard
    from tests.utils._c_bindings import read_clipboard
else:
    pytest.skip(ONLY_ON_WINDOWS, allow_module_level=True)

    # mypy
    read_buffer_as_base64_and_copy_to_clipboard = lambda _: ""
    read_clipboard = lambda: ""


def test_read_buffer_as_base64_and_copy_to_clipboard() -> None:
    image_buffer = read_image_into_buffer(EXAMPLE_WEBP_PATH)
    assert image_buffer is not None, "Failed to setup image buffer"

    read_buffer_as_base64_and_copy_to_clipboard(image_buffer)

    assert (
        read_clipboard()
        == "A=lGRjwAAABXRUJQVlA4IDAAAADwAQCdASoCAAIAAMASJQBOl0AAY0NZ7kAA/vFJbWUuQA8mfXnqY4v+LaR0KTwAAA"  # noqa: E501
    )
