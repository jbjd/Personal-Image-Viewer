"""Handling of uncaught exceptions."""

from types import TracebackType


def exception_hook(
    error_type: type[BaseException],
    error: BaseException,
    trace: TracebackType | None,
) -> None:
    """Writes unhandled fatal exception to file."""
    import traceback

    try:  # Try to write, but don't allow another exception since that may be confusing
        with open("ERROR.log", "w", encoding="utf-8") as fp:
            traceback.print_exception(error_type, error, trace, file=fp)
    except OSError:
        pass
