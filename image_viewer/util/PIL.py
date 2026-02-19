# noqa: N999
"""Functions for manipulating PIL and PIL's image objects"""

import os
from textwrap import wrap
from typing import IO

from PIL import Image as _Image  # avoid name conflicts
from PIL.Image import Image, Resampling, Transpose, new, register_open
from PIL.ImageDraw import ImageDraw
from PIL.ImageFont import FreeTypeFont
from PIL.JpegImagePlugin import JpegImageFile

from image_viewer.constants import TEXT_RGB, Rotation

if os.name == "nt":
    from image_viewer.util._os_nt import get_files_in_folder

# Modes that need more descriptive names or who's bpp
# does not follow len(mode) * 8
_mode_info_special_cases: dict[str, tuple[str, int]] = {
    "I": ("Signed Integer Pixels", 32),
    "L": ("Grayscale", 8),
    "LA": ("Grayscale With Alpha", 16),
    "P": ("Palette", 8),
    "PA": ("Palette With Alpha", 16),
    "1": ("Black And White", 1),
}

_modes_with_alpha: tuple[str, str] = ("RGBA", "LA")


def get_mode_info(mode: str) -> tuple[str, int]:
    """Given a PIL image's mode, return additional info on it.

    Certain modes aren't supported by this program and will not be handled.
    YCbCr: Only used for JPEG 2000, which is unsupported.
    HSV: No docs indicate that this can be used for opening or saving.
    F: Only used for TIFF format, which is unsupported.

    :param mode: Mode of a PIL image.
    :returns: A readable name and the bits per pixels"""

    return (
        _mode_info_special_cases[mode]
        if mode in _mode_info_special_cases
        else (mode, len(mode) * 8)
    )


def rotate_image(image: Image, angle: Rotation) -> Image:
    """Rotates an image with the highest quality"""
    match angle:
        case Rotation.DOWN:
            return image.transpose(Transpose.ROTATE_180)
        case Rotation.RIGHT:
            return image.transpose(Transpose.ROTATE_270)
        case Rotation.LEFT:
            return image.transpose(Transpose.ROTATE_90)
        case _:
            return image


def image_is_animated(image: Image) -> bool:
    """Checks if PIL Image is animated.

    :param image: A PIL Image.
    :returns: True if image is animated."""

    return getattr(image, "is_animated", False)


def resize(
    image: Image, size: tuple[int, int], resample: Resampling = Resampling.LANCZOS
) -> Image:
    """Modified version of resize from PIL"""
    image.load()
    if image.size == size:
        return image.copy()

    box: tuple[int, int, int, int] = (0, 0, *image.size)
    original_mode: str = image.mode
    modes_to_convert: dict[str, str] = {
        "RGBA": "RGBa",
        "LA": "La",
        "P": "RGB",
        "1": "RGB",
    }

    if original_mode in modes_to_convert:
        new_mode: str = modes_to_convert[original_mode]
        image = image.convert(new_mode)

    resized_image: Image = image._new(image.im.resize(size, resample, box))

    # These mode were temporarily converted to pre-compute alpha and should be reverted
    if original_mode in _modes_with_alpha:
        resized_image = resized_image.convert(original_mode)

    return resized_image


def optimize_image_mode(image: Image) -> Image:
    """Optimizes a PIL Image by removing useless color channels.

    :param image: PIL Image to optimize
    :returns: New PIL Image with optimized mode or original if already optimal"""

    if _has_useless_alpha_channel(image):
        image = image.convert(image.mode[:-1])

    if _should_be_grayscale(image):
        image = image.convert("L")

    return image


def _has_useless_alpha_channel(image: Image) -> bool:
    """Checks if a PIL Image's alpha channel is all value 255.

    :param image: PIL Image to check
    :returns: If alpha channel is useless"""
    if image.mode not in _modes_with_alpha:
        return False

    image.load()
    alpha_distribution: list[int] = image.im.split()[-1].histogram()
    return (
        all(alpha_distribution[i] == 0 for i in range(254))
        and alpha_distribution[255] > 0
    )


def _should_be_grayscale(image: Image) -> bool:
    """Checks if a PIL Image only uses grayscale.

    :param image: PIL Image to check
    :returns: If PIL Image should be grayscale"""
    if image.mode != "RGB":
        return False

    colors: list[tuple[int, tuple[int, int, int]]] | None = image.getcolors()  # type: ignore[assignment]
    return colors is not None and all(rgb[0] == rgb[1] == rgb[2] for _, rgb in colors)


def _get_longest_line_dimensions(text: str) -> tuple[int, int]:
    """Returns width and height of longest string in a string with multiple lines"""
    longest_line: str = max(text.split("\n"), key=len)

    width_offset, height_offset, width, height = ImageDraw.font.getbbox(longest_line)  # type: ignore[union-attr]

    return int(width + width_offset), int(height + height_offset)


def create_dropdown_image(text: str) -> Image:
    """Creates a new Image with current images metadata"""
    line_width, line_height = _get_longest_line_dimensions(text)

    line_count: int = text.count("\n") + 1
    line_spacing: int = round(line_height * 0.8)

    x_padding: int = max(int(line_width * 0.14), 20)
    y_padding: int = line_spacing * (line_count + 1)

    width: int = line_width + x_padding
    height: int = (line_height * line_count) + y_padding

    dropdown_rgba: tuple[int, int, int, int] = (40, 40, 40, 170)
    image: Image = new("RGBA", (width, height), dropdown_rgba)

    draw: ImageDraw = ImageDraw(image)
    draw.text((10, line_spacing), text, fill="white", spacing=line_spacing)

    return draw._image


def get_placeholder_for_errored_image(
    error: Exception, screen_width: int, screen_height: int
) -> Image:
    """Returns an Image with error message"""
    error_type: str = type(error).__name__
    error_title: str = f"{error_type} occurred while trying to load file"

    # Wrap each individual line, then join to preserve already existing new lines
    error_text: str = str(error)
    formatted_error: str = "\n\n".join(
        "\n".join(wrap(line, 100)) for line in error_text.split("\n")
    ).capitalize()

    # Placeholder is black with brownish line going diagonally across
    blank_image: Image = new("RGB", (screen_width, screen_height))
    draw: ImageDraw = ImageDraw(blank_image)
    line_rgb: tuple[int, int, int] = (30, 20, 20)
    line_width: int = int((screen_width / 1920) * 100)
    draw.line((0, 0, screen_width, screen_height), line_rgb, width=line_width)

    # Write title
    *_, w, h = ImageDraw.font.getbbox(error_title)  # type: ignore[union-attr]
    y_offset: int = screen_height - int(h * (5 + formatted_error.count("\n"))) >> 1
    x_offset: int = int(screen_width - w) >> 1
    draw.text((x_offset, y_offset), error_title, TEXT_RGB)

    # Write error body 2 lines of height below title
    w, h = _get_longest_line_dimensions(formatted_error)
    y_offset += h * 2
    x_offset = (screen_width - w) >> 1
    draw.text((x_offset, y_offset), formatted_error, TEXT_RGB)

    return draw._image


def _preinit() -> None:
    """Edited version of PIL's preinit to be used as a replacement"""
    if _Image._initialized > 0:
        return

    __import__("PIL.AvifImagePlugin", globals(), {}, ())
    __import__("PIL.JpegImagePlugin", globals(), {}, ())
    __import__("PIL.GifImagePlugin", globals(), {}, ())
    __import__("PIL.PngImagePlugin", globals(), {}, ())
    __import__("PIL.WebPImagePlugin", globals(), {}, ())
    __import__("PIL.DdsImagePlugin", globals(), {}, ())

    def new_jpeg_factory(
        fp: IO[bytes], filename: str | bytes | None = None
    ) -> JpegImageFile:
        return JpegImageFile(fp, filename)

    register_open(
        "JPEG", new_jpeg_factory, lambda prefix: prefix[:3] == b"\xff\xd8\xff"
    )

    _Image._initialized = 2


def _stop_unwanted_PIL_imports() -> None:  # noqa: N802
    """Edits parts of PIL module to prevent excessive imports"""
    from PIL.JpegImagePlugin import MARKER, Skip

    # Remove calls to "APP" since its only for exif and uses removed Tiff plugin
    # Can't edit APP directly due to PIL storing it in this dict
    for i in range(0xFFE0, 0xFFF0):
        # ICC color profile info
        if i == 0xFFE2:
            continue

        MARKER[i] = ("", "", Skip)

    del MARKER, Skip

    # Edit plugins and preinit to avoid importing many unused image modules
    _Image._plugins = []
    _Image.preinit = _preinit


def init_PIL(font_file: str, font_size: int) -> None:  # noqa: N802
    """Sets up font and edit PIL's internal list of plugins to load"""

    _stop_unwanted_PIL_imports()

    ImageDraw.font = _get_PIL_font(font_file, font_size)


def _get_PIL_font(font_file: str, font_size: int) -> FreeTypeFont:  # noqa: N802
    """Returns font for PIL to use."""

    font_folder: str
    if os.name == "nt":
        windir: str | None = os.environ.get("WINDIR")
        if windir:
            font_folder = os.path.join(windir, "fonts")
            for file in get_files_in_folder(font_folder):
                if file == font_file:
                    return FreeTypeFont(os.path.join(font_folder, font_file), font_size)
    else:
        data_home: str | None = os.environ.get("XDG_DATA_HOME")
        if not data_home:
            data_home = os.path.expanduser("~/.local/share")

        data_dirs: str | None = os.environ.get("XDG_DATA_DIRS")
        if not data_dirs:
            data_dirs = "/usr/local/share:/usr/share"

        parent_folders: list[str] = [data_home, *data_dirs.split(":")]
        font_folders: list[str] = [os.path.join(p, "fonts") for p in parent_folders]

        for font_folder in font_folders:
            for root_folder, __, files in os.walk(font_folder):
                for file in files:
                    if file == font_file:
                        return FreeTypeFont(
                            os.path.join(root_folder, font_file), font_size
                        )

    raise RuntimeError(f"Can't find font {font_file}, try adjusting config.ini")
