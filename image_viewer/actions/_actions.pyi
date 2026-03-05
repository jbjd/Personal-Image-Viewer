class FileAction:
    """Abstract class that can't be instantiated.

    Used to track actions done to a file."""

    __slots__ = ("original_path",)

    original_path: str

class Rename(FileAction):
    """Represents a file path changing"""

    __slots__ = ("new_path",)

    new_path: str

    def __init__(self, original_path: str, new_path: str, /) -> None: ...

class Convert(Rename):
    """Represents a conversion done to a file such that a new path exists,
    but it is related to the old path. Such as converting an image where both
    the old and converted image now exist"""

    __slots__ = ("original_file_deleted",)

    original_file_deleted: bool

    def __init__(
        self, original_path: str, new_path: str, original_file_deleted: bool
    ) -> None: ...

class Delete(FileAction):
    """Represents a file being deleted and sent to the recycle bin"""

    __slots__ = ()

    def __init__(self, original_path: str) -> None: ...
