import pytest

from image_viewer.constants import Movement
from image_viewer.image.file import ImageName, ImageNameList


@pytest.mark.parametrize(
    "index_movement,starting_index,expected_index",
    [
        (Movement.BACKWARD, 0, 3),
        (Movement.NONE, 0, 0),
        (Movement.FORWARD, 0, 0),
        (Movement.BACKWARD, 2, 1),
        (Movement.NONE, 2, 2),
        (Movement.FORWARD, 2, 2),
        (Movement.BACKWARD, 4, 3),
        (Movement.NONE, 4, 3),
        (Movement.FORWARD, 4, 0),
    ],
)
def test_remove_current_image(
    index_movement: Movement, starting_index: int, expected_index: int
):
    image_names = ImageNameList(
        [
            ImageName("a.png"),
            ImageName("b.png"),
            ImageName("c.png"),
            ImageName("d.png"),
            ImageName("e.png"),
        ]
    )
    image_names._display_index = starting_index

    image_names.remove_current_image(index_movement)

    assert image_names._display_index == expected_index
