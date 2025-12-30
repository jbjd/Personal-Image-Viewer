class FileAction:
    """Can't be instantiated.

    Used to track actions done to a file."""

    __slots__ = ("original_path",)

    def __init__(self, original_path: str, /) -> None:
        self.original_path: str = original_path

class UIElementBase:
    """Can't be instantiated.

    Base class for any element on a tkinter canvas."""

    __slots__ = ("id",)

    def __init__(self, id: int = -1) -> None:
        self.id = id
