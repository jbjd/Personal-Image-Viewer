import re
from time import perf_counter

from image_viewer.util._generic import is_valid_keybind

tests = [
    "asdvbiu34uiyaiwyt47ybtv18nc98177841ync8397cn1789crt12978xrnwegfg",
    "<Control-d>",
    "<Control-F0>",
    "<Control-F6>",
    "<Control->",
    "<F0>",
    "<F1>",
    "<F12>",
    "<F13>",
    "<F91>",
    "<A>",
]
unique_count: int = len(tests)

tests *= 99999


is_valid_keybind_re = re.compile(
    "^<((Control-)?([A-Z]|F[1-9]|F1[0-2])|Control-[a-z0-9])>$"
)


def validate_keybind_or_default_python(keybind, default):
    match = is_valid_keybind_re.match(keybind)

    return default if match is None else keybind


def validate_keybind_or_default_c(keybind, default):
    return keybind if is_valid_keybind(keybind) else default


def run():
    a = perf_counter()

    python_results: list[str] = [
        validate_keybind_or_default_python(t, "") for t in tests
    ]

    print("Python time:", perf_counter() - a)

    a = perf_counter()

    c_results: list[str] = [validate_keybind_or_default_c(t, "") for t in tests]

    print("C time:", perf_counter() - a)

    assert python_results == c_results, (
        f"{python_results[:unique_count]} != {c_results[:unique_count]}"
    )
