from collections.abc import Callable
from time import perf_counter


class PerfTest[**P, PYTHON_RETURN, C_RETURN]:
    __slots__ = ("c_implementation", "python_implementation")

    def __init__(
        self,
        python_implementation: Callable[P, PYTHON_RETURN],
        c_implementation: Callable[P, C_RETURN],
    ) -> None:
        self.python_implementation: Callable[P, PYTHON_RETURN] = python_implementation
        self.c_implementation: Callable[P, C_RETURN] = c_implementation

    def run(
        self,
        description: str,
        iterations: int,
        assert_function: Callable[[PYTHON_RETURN, C_RETURN], None],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        a = perf_counter()

        for _ in range(iterations):
            python_result: PYTHON_RETURN = self.python_implementation(*args, **kwargs)

        print(f"({description}) Python time:", perf_counter() - a)

        a = perf_counter()

        for _ in range(iterations):
            c_result: C_RETURN = self.c_implementation(*args, **kwargs)

        print(f"({description}) C time:", perf_counter() - a)

        assert_function(python_result, c_result)
