from collections.abc import Callable
from time import perf_counter
from tkinter import Event, Tk
from typing import NoReturn

from PIL.Image import Image
from PIL.ImageTk import PhotoImage


class ViewerApp:

    def __init__(self) -> None:
        self.app: Tk = self._setup_tk_app()

    @staticmethod
    def _setup_tk_app() -> Tk:
        """Creates and setups Tk class"""
        app: Tk = Tk()

        return app

    def start(self) -> None:
        """Starts tkinter main loop"""
        self.app.mainloop()
