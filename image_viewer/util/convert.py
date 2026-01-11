"""Conversion between image file types and representations."""

import binascii
from typing import IO

from PIL.Image import Image
from PIL.Image import open as open_image
from PIL.JpegImagePlugin import RAWMODE as VALID_JPEG_MODES

from image_viewer.constants import VALID_FILE_TYPES
from image_viewer.image.file import magic_number_guess
from image_viewer.util.PIL import image_is_animated, save_image


def try_convert_file_and_save_new(
    old_path: str, new_path: str | IO[bytes], target_format: str, quality: int = 90
) -> bool:
    """Tries to convert image at old_path to a target format at new_path.

    :param old_path: Existing path to an image.
    :apram new_path: Path to save the new image to.
    :param target_format: Format to convert to.
    :returns: bool if conversion performed successfully.
    :raises ValueError: If converting animated file to non-animated format."""

    target_format = target_format.lower()

    if target_format not in VALID_FILE_TYPES:
        return False

    with open(old_path, "rb") as fp:
        original_ext: str = magic_number_guess(fp.read(4))

        # Only first letter checked since jpeg is the only supported file extension
        # that has multiple variations and all start with 'j'
        if target_format[0] == original_ext[0].lower():
            return False

        temp_img: Image
        with open_image(fp) as temp_img:
            is_animated: bool = image_is_animated(temp_img)
            if is_animated and target_format not in ("webp", "gif", "png"):
                raise ValueError

            if target_format in ("jpg", "jpeg", "jif", "jfif", "jpe"):
                target_format = "jpeg"
                if temp_img.mode not in VALID_JPEG_MODES:
                    temp_img = temp_img.convert("RGB")  # noqa: PLW2901
            elif (
                target_format == "gif"
                and original_ext == "webp"
                and "background" in temp_img.info
            ):
                # This pop fixes missing bitmap error during webp -> gif conversion
                del temp_img.info["background"]

            save_image(
                temp_img,
                new_path,
                target_format,
                quality,
                is_animated=is_animated,
                icc_profile=temp_img.info.get("icc_profile"),
            )

    return True


def read_memory_as_base64(image_buffer: memoryview) -> str:
    """Decodes some memory into a base64 string.

    :param image_buffer: The memory buffer of an image to decode.
    :returns: The decoded base64."""

    return binascii.b2a_base64(image_buffer, newline=False).decode(
        "ascii", errors="ignore"
    )
