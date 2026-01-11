"""Classes representing button UI elements"""

from collections.abc import Callable
from tkinter import Event
from typing import override

from PIL.ImageTk import PhotoImage

from image_viewer.constants import ButtonName
from image_viewer.ui.base import ButtonUIElementBase
from image_viewer.ui.canvas import CustomCanvas


class IconImages:
    """Icons for on-screen buttons with a default and a hovered image."""

    __slots__ = ("default", "hovered")

    def __init__(self, default: PhotoImage, hovered: PhotoImage) -> None:
        self.default = default
        self.hovered = hovered


class HoverableButtonUIElement(ButtonUIElementBase):
    """Button with different icons when its hovered"""

    __slots__ = ("canvas", "icon", "icon_hovered", "on_click_function")

    def __init__(
        self,
        canvas: CustomCanvas,
        icon: IconImages,
        on_click_function: Callable[[], None],
    ) -> None:
        super().__init__()
        self.canvas: CustomCanvas = canvas
        self.icon: PhotoImage = icon.default
        self.icon_hovered: PhotoImage = icon.hovered
        self.on_click_function: Callable[[], None] = on_click_function

    def create(self, name: ButtonName, x_offset: int = 0, y_offset: int = 0) -> None:
        """Adds self to canvas.

        :param name: The name to associate to this button.
        :param x_offset: The on-screen X offset.
        :param y_offset: The on-screen Y offset."""

        self.id = self.canvas.create_button(
            self, name, x_offset, y_offset, image=self.icon
        )

        self.canvas.tag_bind(self.id, "<Enter>", self.on_enter)
        self.canvas.tag_bind(self.id, "<Leave>", self.on_leave)
        self.canvas.tag_bind(self.id, "<ButtonRelease-1>", self.on_click)

    @override
    def on_click(self, event: Event | None = None) -> None:
        """Calls the on-click function."""

        self.on_click_function()

    @override
    def on_enter(self, _: Event | None = None) -> None:
        """Updates display icon with return value from :func:`_get_hovered_icon`"""

        self.canvas.itemconfigure(self.id, image=self._get_hovered_icon())

    @override
    def on_leave(self, _: Event | None = None) -> None:
        """Updates display icon with return value from :func:`_get_default_icon`"""

        self.canvas.itemconfigure(self.id, image=self._get_default_icon())

    def _get_hovered_icon(self) -> PhotoImage:
        """Gets the hovered icon. Can be override by subclasses to change on hover icon
        based on state.

        :returns: The hovered icon."""

        return self.icon_hovered

    def _get_default_icon(self) -> PhotoImage:
        """Gets the default icon. Can be override by subclasses to change default icon
        based on state.

        :returns: The default icon."""

        return self.icon


class ToggleableButtonUIElement(HoverableButtonUIElement):
    """Extends HoverableButtonUIElement by allowing an active/inactive state."""

    __slots__ = ("active_icon", "active_icon_hovered", "is_active")

    def __init__(
        self,
        canvas: CustomCanvas,
        icon: IconImages,
        active_icon: IconImages,
        on_click_function: Callable[[], None],
    ) -> None:
        super().__init__(canvas, icon, on_click_function)
        self.active_icon: PhotoImage = active_icon.default
        self.active_icon_hovered: PhotoImage = active_icon.hovered
        self.is_active: bool = False

    @override
    def on_click(self, event: Event | None = None) -> None:
        """Toggles between active state and calls the on-click function."""
        self.is_active = not self.is_active
        self.on_enter()  # fake mouse hover
        super().on_click()

    @override
    def _get_hovered_icon(self) -> PhotoImage:
        """Gets correct hovered icon based on active state.

        :returns: Either the active or regular hovered icon icon depending on state."""

        return self.active_icon_hovered if self.is_active else self.icon_hovered

    @override
    def _get_default_icon(self) -> PhotoImage:
        """Gets correct default icon based on active state.

        :returns: Either the active or regular default icon icon depending on state."""

        return self.active_icon if self.is_active else self.icon
