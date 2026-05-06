from PIL.Image import Image

from image_viewer.image.frame import DEFAULT_ANIMATION_SPEED_MS, AnimationFrame


def test_get_ms_until_next_frame():
    example_image = Image()
    frame = AnimationFrame(example_image)

    assert frame.get_ms_until_next_frame(example_image) == DEFAULT_ANIMATION_SPEED_MS

    example_image.info = {"duration": 67}
    assert frame.get_ms_until_next_frame(example_image) == 67
