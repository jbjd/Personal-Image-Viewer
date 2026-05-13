from collections.abc import Callable
from time import perf_counter
from typing import TypeVar, TypeVarTuple

_Ts = TypeVarTuple("_Ts")
PYTHON_RETURN = TypeVar("PYTHON_RETURN")
C_RETURN = TypeVar("C_RETURN")


class PerfTest:
    __slots__ = ("c_implementation", "python_implementation")

    def __init__(
        self,
        python_implementation: Callable[[*_Ts], PYTHON_RETURN],
        c_implementation: Callable[[*_Ts], C_RETURN],
    ) -> None:
        self.python_implementation: Callable = python_implementation
        self.c_implementation: Callable = c_implementation

    def run(
        self,
        description: str,
        iterations: int,
        assert_function: Callable[[PYTHON_RETURN, C_RETURN], None],
        *args: *_Ts,
    ) -> None:
        a = perf_counter()

        for _ in range(iterations):
            python_result: PYTHON_RETURN = self.python_implementation(*args)

        print(f"({description}) Python time:", perf_counter() - a)

        a = perf_counter()

        for _ in range(iterations):
            c_result: C_RETURN = self.c_implementation(*args)

        print(f"({description}) C time:", perf_counter() - a)

        assert_function(python_result, c_result)
