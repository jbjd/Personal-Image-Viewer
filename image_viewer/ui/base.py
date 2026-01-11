"""Base classes for UI elements on a tkinter canvas."""

from abc import abstractmethod
from tkinter import Event


class UIElementBase:
    """Base class for any element on a tkinter canvas."""

    __slots__ = ("id",)

    @abstractmethod
    def __init__(self, canvas_id: int = -1) -> None:
        self.id: int = canvas_id


class ButtonUIElementBase(UIElementBase):
    """Base class for buttons on a tkinter canvas."""

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def on_click(self, event: Event | None = None) -> None:
        """Function to run when button clicked"""

    def on_enter(self, _: Event | None = None) -> None:
        """Function to run when mouse first hovers the button"""

    def on_leave(self, _: Event | None = None) -> None:
        """Function to run when mouse first leaves hovering the button"""
