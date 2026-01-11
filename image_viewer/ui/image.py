"""Classes that represent images on a tkinter canvas"""

from PIL.ImageTk import PhotoImage

from image_viewer.ui.base import UIElementBase


class ImageUIElement(UIElementBase):
    """Represents an image displayed on a tkinter canvas"""

    __slots__ = ("image",)

    def __init__(self, image: PhotoImage | None, canvas_id: int) -> None:
        super().__init__(canvas_id)
        self.image: PhotoImage | None = image


class DropdownImageUIElement(ImageUIElement):
    """Represents a lazy loaded drop down image displayed on a tkinter canvas"""

    __slots__ = ("need_refresh", "show")

    def __init__(self, canvas_id: int) -> None:
        super().__init__(None, canvas_id)
        self.need_refresh: bool = True
        self.show: bool = False

    def toggle_display(self) -> None:
        """Flips if showing is true or false"""
        self.show = not self.show
