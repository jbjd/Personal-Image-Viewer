from tkinter import Event, Tk
from typing import NoReturn


class ViewerApp:

    def __init__(self) -> None:
        self.app: Tk = self._setup_tk_app()

    @staticmethod
    def _setup_tk_app() -> Tk:
        """Creates and setups Tk class"""
        app: Tk = Tk()

        return app
