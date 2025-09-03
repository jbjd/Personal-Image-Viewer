"""Entrypoint for the lightweight personal image viewer."""

import sys
from types import TracebackType


def exception_hook(
    error_type: type[BaseException],
    error: BaseException,
    trace: TracebackType | None,
    destination_folder: str,
) -> None:
    """Writes unhandled fatal exception to file."""
    import os
    import traceback

    error_file: str = os.path.join(destination_folder, "ERROR.log")

    try:  # Try to write, but don't allow another exception since that may be confusing
        with open(error_file, "w", encoding="utf-8") as fp:
            traceback.print_exception(error_type, error, trace, file=fp)
    except OSError:
        pass


if __name__ == "__main__" and len(sys.argv) > 1:  # pragma: no cover
    from util.os import get_path_to_exe_folder
    from viewer import ViewerApp

    path_to_exe_folder: str = get_path_to_exe_folder()

    if not __debug__:
        sys.excepthook = lambda error_type, error, trace: exception_hook(
            error_type, error, trace, path_to_exe_folder
        )

    ViewerApp(sys.argv[1], path_to_exe_folder).start()
