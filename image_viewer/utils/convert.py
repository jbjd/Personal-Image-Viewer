"""Conversion between image file types and representations."""

import binascii

from PIL.Image import Image
from PIL.ImageSequence import Iterator as ImageIterator
from PIL.JpegImagePlugin import RAWMODE as VALID_JPEG_MODES

from image_viewer.constants import VALID_FILE_TYPES
from image_viewer.image.frame import DEFAULT_ANIMATION_SPEED_MS
from image_viewer.utils.PIL import image_is_animated


def try_convert_image_and_save_new(
    original_image: Image,
    original_format: str,
    new_path: str,
    target_format: str,
    quality: int = 96,
) -> bool:
    """Tries to convert image at old_path to a target format at new_path.

    :param original_image: PIL image to convert
    :
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

    save_kwargs: dict = {
        "optimize": True,
        "quality": quality,
        "icc_profile": original_image.info.get("icc_profile"),
    }

    if image_is_animated(original_image):
        if target_format not in ("webp", "gif", "png"):
            raise ValueError

        save_kwargs["save_all"] = True
        save_kwargs["loop"] = original_image.info.get("loop", 0)

        save_kwargs["duration"] = [
            frame.info.get("duration", DEFAULT_ANIMATION_SPEED_MS)
            for frame in ImageIterator(original_image)
        ]

    image_to_save: Image = original_image.copy()

    match target_format:
        case "avif":
            save_kwargs["speed"] = 0
        case "jpg" | "jpeg" | "jif" | "jfif" | "jpe":
            target_format = "jpeg"
            if image_to_save.mode not in VALID_JPEG_MODES:
                image_to_save = image_to_save.convert("RGB")
        case "gif":
            if original_format == "webp" and "background" in image_to_save.info:
                # This pop fixes missing bitmap error
                del image_to_save.info["background"]
        case "webp":
            save_kwargs["method"] = 6

    image_to_save.save(new_path, target_format, **save_kwargs)

    return True


def read_memory_as_base64(image_buffer: memoryview) -> str:
    """Decodes some memory into a base64 string.

    :param image_buffer: The memory buffer of an image to decode.
    :returns: The decoded base64."""

    return binascii.b2a_base64(image_buffer, newline=False).decode(
        "ascii", errors="ignore"
    )
