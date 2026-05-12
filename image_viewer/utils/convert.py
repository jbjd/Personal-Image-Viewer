"""Conversion between image file types and representations."""

import binascii

from PIL.Image import Image
from PIL.Image import open as open_image
from PIL.ImageSequence import Iterator as ImageIterator
from PIL.JpegImagePlugin import RAWMODE as VALID_JPEG_MODES

from image_viewer.constants import VALID_FILE_TYPES
from image_viewer.image.frame import DEFAULT_ANIMATION_SPEED_MS
from image_viewer.utils.PIL import image_is_animated


def try_convert_file_and_save_new(
    old_path: str,
    new_path: str,
    original_format: str,
    target_format: str,
    quality: int = 96,
) -> bool:
    """Tries to convert image at old_path to a target format at new_path.

    :param old_path: Existing path to an image
    :apram new_path: Path to save the new image to
    :param target_format: Format to convert to
    :param quality: Quality 0-100 to pass to encoder
    :returns: bool if conversion performed successfully
    :raises ValueError: If converting animated file to non-animated format"""

    original_format = original_format.lower()
    target_format = target_format.lower()

    # Only first letter checked since jpeg is the only supported file extension
    # that has multiple variations and all start with 'j'
    if target_format not in VALID_FILE_TYPES or original_format[0] == target_format[0]:
        return False

    temp_img: Image
    with open_image(old_path) as temp_img:
        save_kwargs: dict = {
            "optimize": True,
            "quality": quality,
            "icc_profile": temp_img.info.get("icc_profile"),
        }

        if image_is_animated(temp_img):
            if target_format not in ("webp", "gif", "png"):
                raise ValueError

            save_kwargs["save_all"] = True
            save_kwargs["loop"] = temp_img.info.get("loop", 0)

            save_kwargs["duration"] = [
                frame.info.get("duration", DEFAULT_ANIMATION_SPEED_MS)
                for frame in ImageIterator(temp_img)
            ]

        match target_format:
            case "avif":
                save_kwargs["speed"] = 0
            case "jpg" | "jpeg" | "jif" | "jfif" | "jpe":
                target_format = "jpeg"
                if temp_img.mode not in VALID_JPEG_MODES:
                    temp_img = temp_img.convert("RGB")  # noqa: PLW2901
            case "gif":
                if original_format == "webp" and "background" in temp_img.info:
                    # This pop fixes missing bitmap error
                    del temp_img.info["background"]
            case "webp":
                save_kwargs["method"] = 6

        temp_img.save(new_path, target_format, **save_kwargs)

    return True


def read_memory_as_base64(image_buffer: memoryview) -> str:
    """Decodes some memory into a base64 string.

    :param image_buffer: The memory buffer of an image to decode.
    :returns: The decoded base64."""

    return binascii.b2a_base64(image_buffer, newline=False).decode(
        "ascii", errors="ignore"
    )
