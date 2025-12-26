"""Constants needed in multiple spots of the codebase."""

from enum import IntEnum, StrEnum
from typing import Iterable


class ImageFormats(StrEnum):
    """Image formats that this program supports."""

    AVIF = "avif"
    DDS = "dds"
    GIF = "gif"
    JFIF = "jfif"
    JIF = "jif"
    JPE = "jpe"
    JPEG = "jpeg"
    JPG = "jpg"
    PNG = "png"
    WEBP = "webp"


class Key(IntEnum):
    """Tkinter keysym numbers."""

    LEFT = 65361
    RIGHT = 65363
    DOWN = 65364


class Rotation(IntEnum):
    """Angles the image can be rotated."""

    UP = 0
    LEFT = 90
    DOWN = 180
    RIGHT = 270


class ZoomDirection(IntEnum):
    """Direction for the zoom movement."""

    IN = 1
    OUT = -1


class Movement(IntEnum):
    """Common movement amounts between images."""

    FORWARD = 1
    NONE = 0
    BACKWARD = -1


class TkTags(StrEnum):
    """Tags for items on the UI."""

    TOPBAR = "topbar"
    BACKGROUND = "back"


class ButtonName(StrEnum):
    """Names of buttons on the UI."""

    EXIT = "exit"
    MINIFY = "minify"
    TRASH = "trash"
    RENAME = "rename"
    DROPDOWN = "dropdown"


VALID_FILE_TYPES: Iterable[str] = ImageFormats.__members__.values()


TEXT_RGB: str = "#FEFEFE"
