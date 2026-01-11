"""Utilities for exception handling in tests"""

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec

_P = ParamSpec("_P")


def safe_wrapper(function: Callable[_P, None]):  # noqa: UP047
    """Given a Callable that returns None, pass if Exception is raised"""

    @wraps(function)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> None:
        try:
            function(*args, **kwargs)
        except Exception:  # noqa: BLE001
            pass

    return wrapper
