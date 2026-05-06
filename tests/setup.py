from tkinter import Tk

_tk_app: Tk = None


def setup_tk() -> Tk:
    """Sets up singleton instance of Tk for testing."""
    global _tk_app

    if _tk_app is None:
        _tk_app = Tk()
        _tk_app.withdraw()

    return _tk_app
