ifeq ($(OS),Windows_NT)
	override DEFAULT_PYTHON := python
	override PYTHON_DLL := python312
	override COMPILED_EXT = pyd
	override EXECUTABLE_EXT=exe
	override OS_FLAGS =
else
	override DEFAULT_PYTHON := python3.12
	override PYTHON_DLL := python3.12
	override COMPILED_EXT = so
	override EXECUTABLE_EXT=bin
	override OS_FLAGS = -fPIC
endif

ifneq (,$(wildcard .venv))  # If .venv folder exists, use that
	ifeq ($(OS),Windows_NT)
		PYTHON_EXECUTABLE = .\\.venv\\Scripts\\$(DEFAULT_PYTHON).exe
	else
		PYTHON_EXECUTABLE = .venv/bin/$(DEFAULT_PYTHON)
	endif
else
	PYTHON_EXECUTABLE = $(DEFAULT_PYTHON)
endif

# Base prefix ignores venv
override PYTHON_BASE_PREFIX := $(shell $(PYTHON_EXECUTABLE) -sSc "import sys;print(sys.base_prefix)")

# Install step python may be venv or not
# But for compiling C we need to use the real python installation
ifeq ($(OS),Windows_NT)
	PYTHON_LIBS = $(PYTHON_BASE_PREFIX)/libs/
	PYTHON_INCLUDES = $(PYTHON_BASE_PREFIX)/include/
else
	PYTHON_LIBS = $(PYTHON_BASE_PREFIX)/libs/python3.12/
	PYTHON_INCLUDES = $(PYTHON_BASE_PREFIX)/include/python3.12/
endif

OPTIMIZATION_FLAG = -O3
EXTRA_C_FLAGS = -Wall -Werror
override NATIVE_FLAGS := -march=native -mtune=native
override C_SOURCE = image_viewer/c_extensions
override C_PYTHON_MODULES = $(C_SOURCE)/python_modules
override C_FLAGS = -L$(PYTHON_LIBS) -I$(PYTHON_INCLUDES) -l$(PYTHON_DLL) $(OPTIMIZATION_FLAG) $(NATIVE_FLAGS) -shared $(OS_FLAGS) -flto -ffinite-math-only -fgcse-las -fgcse-sm -fisolate-erroneous-paths-attribute -fno-signed-zeros -frename-registers -fsched-pressure -s $(EXTRA_C_FLAGS)

build-config:
	gcc $(C_PYTHON_MODULES)/config.c $(C_SOURCE)/config.c $(C_FLAGS) -I$(C_SOURCE) -o image_viewer/_config.$(COMPILED_EXT)

build-image-read:
	gcc $(C_PYTHON_MODULES)/image_read.c $(C_FLAGS) -I$(C_SOURCE) -o image_viewer/image/_read.$(COMPILED_EXT) -lturbojpeg

build-util-os-nt:
ifeq ($(OS),Windows_NT)
	gcc $(C_PYTHON_MODULES)/utils_os_nt.c $(C_SOURCE)/b64/base64.c -I$(C_SOURCE) -lshlwapi -loleaut32 -lole32 $(C_FLAGS) -o image_viewer/utils/_os_nt.$(COMPILED_EXT)
endif

build-test:
	gcc $(C_PYTHON_MODULES)/test_ext.c $(C_SOURCE)/config.c $(C_FLAGS) -I$(C_SOURCE) -o tests/utils/_c_bindings.$(COMPILED_EXT)

build-all: build-config build-image-read build-util-os-nt build-test

build-all-dist: NATIVE_FLAGS=
build-all-dist: build-all

benchmark-c-base64:
	gcc $(C_SOURCE)/tests/benchmark_base64.c $(C_SOURCE)/b64/base64.c -I$(C_SOURCE) -o test
	./test.$(EXECUTABLE_EXT)

test-c-base64:
	gcc $(C_SOURCE)/tests/test_base64.c $(C_SOURCE)/b64/base64.c $(C_SOURCE)/tests/util.c -I$(C_SOURCE) -o test -lcunit -mavx2
	./test.$(EXECUTABLE_EXT)

install:
	$(PYTHON_EXECUTABLE) -OO compile.py --extra-checks --strip

install-dist:
	$(PYTHON_EXECUTABLE) -OO compile.py --extra-checks --strip --distribution

bundle-dist:
	$(PYTHON_EXECUTABLE) -OO compile.py --extra-checks --strip --distribution --install-path ./dist

install-debug:
	$(PYTHON_EXECUTABLE) -OO compile.py --extra-checks --strip --debug

install-debug-setup:
	$(PYTHON_EXECUTABLE) -OO compile.py --extra-checks --debug --skip-nuitka

override C_AND_H_FILES = $(shell $(PYTHON_EXECUTABLE) -sSc "from glob import glob;print(' '.join(glob('image_viewer/**/*.[ch]',recursive=True)))")

format:
	ruff check . --fix
	clang-format -i $(C_AND_H_FILES)

validate:
	ruff check .
	ruff format --check
	clang-format -n -Werror $(C_AND_H_FILES)
	mypy .
	codespell

override PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
export PYTEST_DISABLE_PLUGIN_AUTOLOAD

test:
	$(PYTHON_EXECUTABLE) -m coverage run --source=image_viewer -m pytest --ignore=tests/test_memory_leaks.py
	@coverage report -m

override PYTHONUNBUFFERED=1
export PYTHONUNBUFFERED

test-memory-leak:
	$(PYTHON_EXECUTABLE) -m pytest tests/test_memory_leaks.py
