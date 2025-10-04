"""Handling of uncaught exceptions."""

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
