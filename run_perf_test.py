import importlib
import sys
from types import ModuleType

perf_tests: list[str] = ["keybind"]

if len(sys.argv) < 2 or sys.argv[1] not in perf_tests:
    exit_code: int
    if len(sys.argv) < 2:
        exit_code = 0
    else:
        print("Invalid argument", sys.argv[1])
        exit_code = 1

    print("Runs a performace test, one of:", perf_tests)
    sys.exit(exit_code)

perf_module: ModuleType = importlib.import_module("perf." + sys.argv[1])
perf_module.run()
