"""Utilities for exception handling in tests"""

from collections.abc import Callable
from functools import wraps


def safe_wrapper(function: Callable[..., None]):
    """Given a Callable that returns None, pass if Exception is raised"""

    @wraps(function)
    def wrapper(*args, **kwargs) -> None:
        try:
            function(*args, **kwargs)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    return wrapper
