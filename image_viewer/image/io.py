"""Classes for loading PIL images from disk"""

import os
import tempfile
from collections.abc import Callable
from io import BytesIO
from threading import Thread

from PIL.Image import Image
from PIL.Image import open as open_image

from image_viewer.animation.frame import Frame
from image_viewer.constants import Rotation, ZoomDirection
from image_viewer.image._read import CMemoryViewBuffer, read_image_into_buffer
from image_viewer.image.cache import ImageCache, ImageCacheEntry
from image_viewer.image.file import magic_number_guess
from image_viewer.image.resizer import ImageResizer
from image_viewer.image.state import ZOOM_UNSET, ImageState
from image_viewer.util.PIL import (
    get_placeholder_for_errored_image,
    optimize_image_mode,
    rotate_image,
    save_image,
)


class ReadImageResponse:
    """Response when reading an image from disk"""

    __slots__ = ("expected_format", "image", "image_buffer")

    def __init__(
        self, image_buffer: CMemoryViewBuffer, image: Image, expected_format: str
    ) -> None:
        self.image_buffer: CMemoryViewBuffer = image_buffer
        self.image: Image = image
        self.expected_format: str = expected_format


class ImageIO:
    """Handles image IO."""

    __slots__ = (
        "PIL_image",
        "_image_optimized",
        "_state",
        "animation_callback",
        "animation_frames",
        "current_load_id",
        "frame_index",
        "image_buffer",
        "image_cache",
        "image_resizer",
        "zoomed_image_cache",
    )

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        image_cache: ImageCache,
        animation_callback: Callable[[int, int], None],
    ) -> None:
        self.image_cache: ImageCache = image_cache
        self.image_resizer: ImageResizer = ImageResizer(screen_width, screen_height)

        self.animation_callback: Callable[[int, int], None] = animation_callback

        self.PIL_image = Image()
        self._image_optimized: bool = False
        self.image_buffer: CMemoryViewBuffer
        self.current_load_id: int = 0

        self.animation_frames: list[Frame | None] = []
        self.frame_index: int = 0
        self._state = ImageState()
        self.zoomed_image_cache: list[Image] = []

    @property
    def zoom_rotate_allowed(self) -> bool:
        return self._state.zoom_rotate_allowed

    def get_next_frame(self) -> Frame | None:
        """Gets next frame of animated image or empty frame while its being loaded"""
        try:
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames)
            current_frame = self.animation_frames[self.frame_index]
        except (ZeroDivisionError, IndexError):
            return None

        if current_frame is None:
            self.frame_index -= 1

        return current_frame

    def begin_animation(
        self, original_image: Image, resized_image: Image, frame_count: int
    ) -> None:
        """Begins new thread to load frames of an animated image"""
        self.animation_frames = [None] * frame_count

        first_frame: Frame = Frame(resized_image)
        self.animation_frames[0] = first_frame

        Thread(
            target=self.load_remaining_frames,
            args=(original_image, frame_count, self.current_load_id),
            daemon=True,
        ).start()

        ms_until_next_frame: int = first_frame.ms_until_next_frame
        backoff: int = ms_until_next_frame + 50
        self.animation_callback(ms_until_next_frame, backoff)

    def read_image(self, path_to_image: str) -> ReadImageResponse | None:
        """Tries to open file on disk as PIL Image
        Returns Image or None on failure"""
        try:
            image_buffer: CMemoryViewBuffer | None = read_image_into_buffer(
                path_to_image
            )
            if image_buffer is None:
                return None

            expected_format: str = magic_number_guess(image_buffer.view[:4].tobytes())

            image_bytes_io = BytesIO(image_buffer.view)
            image: Image = open_image(image_bytes_io, "r", (expected_format,))

            return ReadImageResponse(image_buffer, image, expected_format)
        except OSError:
            return None

    def load_image(self, image_path: str) -> Image | None:
        """Loads an image, resizes it to screen, and caches it.
        Returns Image or None on failure"""
        read_image_response: ReadImageResponse | None = self.read_image(image_path)
        if read_image_response is None:
            return None

        original_image: Image = read_image_response.image
        byte_size: int = read_image_response.image_buffer.byte_size

        self.image_buffer = read_image_response.image_buffer
        self.PIL_image = original_image
        self.current_load_id += 1

        # check if cached and not changed outside of program
        resized_image: Image
        cached_image_data = self.image_cache.get(image_path)
        if cached_image_data is not None and byte_size == cached_image_data.byte_size:
            resized_image = cached_image_data.image
        else:
            original_mode: str = original_image.mode
            resized_image = self._resize_or_get_placeholder()

            self.image_cache[image_path] = ImageCacheEntry(
                resized_image,
                original_image.size,
                byte_size,
                original_mode,
                read_image_response.expected_format,
            )

        frame_count: int = getattr(original_image, "n_frames", 1)
        if frame_count > 1:
            self._state.zoom_rotate_allowed = False
            self.begin_animation(original_image, resized_image, frame_count)

        # first zoom level is just the image as is
        self.zoomed_image_cache = [resized_image]

        return resized_image

    def optimize_png_image(self, image_path: str) -> bool:
        """Attempts to optimize the current image's size without affecting quality.
        Only works on PNGs.

        :param image_path: Path to the current image
        :returns: If optimization was performed"""

        image_format: str | None = self.PIL_image.format
        if self._image_optimized or image_format != "PNG":
            return False

        image = optimize_image_mode(self.PIL_image)

        delete_tmp_file: bool = True
        tmp_file = tempfile.NamedTemporaryFile(  # noqa: SIM115
            dir=os.path.dirname(image_path), delete=False
        )
        try:
            with tmp_file:
                save_image(image, tmp_file, image_format, 100)

            original_size: int = self.image_buffer.byte_size
            new_size: int = os.stat(tmp_file.name).st_size

            if new_size > 0 and new_size < original_size:
                os.replace(tmp_file.name, image_path)
                delete_tmp_file = False
                self.PIL_image = image
                self.image_cache.update_value(image_path, new_size, image.mode)

        finally:
            if delete_tmp_file:
                os.remove(tmp_file.name)

        self._image_optimized = True

        # If tmp not deleted, it means we updated original image
        return not delete_tmp_file

    def _resize_or_get_placeholder(self) -> Image:
        """Resizes PIL image or returns placeholder if corrupted in some way"""
        current_image: Image
        try:
            if self.PIL_image.format == "JPEG":
                current_image = self.image_resizer.get_jpeg_fit_to_screen(
                    self.PIL_image, self.image_buffer
                )
            else:
                current_image = self.image_resizer.get_image_fit_to_screen(
                    self.PIL_image
                )
        except OSError as e:
            current_image = get_placeholder_for_errored_image(
                e, self.image_resizer.screen_width, self.image_resizer.screen_height
            )
            self._state.zoom_rotate_allowed = False

        return current_image

    def get_zoomed_or_rotated_image(
        self, direction: ZoomDirection | None, rotation: Rotation | None = None
    ) -> Image | None:
        """Gets current image with orientation changes like zoom and rotation"""
        if __debug__ and not self._state.zoom_rotate_allowed:
            return None

        if self._state.zoom_level_max == ZOOM_UNSET:
            self._state.zoom_level_max = self.image_resizer.get_max_zoom(
                *self.PIL_image.size
            )

        if not self._state.try_update(direction, rotation):
            return None

        zoom_level: int = self._state.zoom_level

        image: Image
        if zoom_level < len(self.zoomed_image_cache):
            image = self.zoomed_image_cache[zoom_level]
        else:
            # Not in cache, resize to new zoom
            try:
                image: Image = self.image_resizer.get_zoomed_image(
                    self.PIL_image,
                    zoom_level,
                    self._state.zoom_level == self._state.zoom_level_max,
                )
            except OSError:
                return None

            self.zoomed_image_cache.append(image)

        return rotate_image(image, self._state.orientation)

    def load_remaining_frames(
        self, original_image: Image, last_frame: int, load_id: int
    ) -> None:
        """Loads all frames starting from the second"""
        for i in range(1, last_frame):
            if load_id != self.current_load_id:
                break
            try:
                original_image.seek(i)
                frame_image: Image = self.image_resizer.get_image_fit_to_screen(
                    original_image
                )

                self.animation_frames[i] = Frame(frame_image)
            except (IndexError, ValueError):
                # Might index into animation_frames incorrectly
                # Or perform action on closed image
                break

    def reset_and_setup(self) -> None:
        """Resets zoom, animation frames, and closes previous image
        to setup for next image load"""
        self._image_optimized = False
        self.animation_frames.clear()
        self.frame_index = 0
        self.PIL_image.close()
        self._state.reset()
        self.zoomed_image_cache.clear()
