ifeq ($(OS),Windows_NT)
    PYTHON = python
	PYTHON_DLL = python312
	COMPILED_EXT = pyd
	OS_FLAGS =
else
    PYTHON = python3.12
	PYTHON_DLL = python3.12
	COMPILED_EXT = so
	OS_FLAGS = -fPIC
endif

# Base prefix ignores venv
PYTHON_BASE_PREFIX := $(shell $(PYTHON) -c "import sys;print(sys.base_prefix)")

ifneq (,$(wildcard .venv))  # If .venv folder exists, use that
	ifeq ($(OS),Windows_NT)
		INSTALL_STEP_PREFIX = .venv/Scripts
	else
		INSTALL_STEP_PREFIX = .venv
	endif
else
    INSTALL_STEP_PREFIX := $(PYTHON_BASE_PREFIX)
endif

# Install step python may be venv or not
# But for compiling C we need to use the real python installation
ifeq ($(OS),Windows_NT)
    PYTHON_FOR_INSTALL_STEP := $(INSTALL_STEP_PREFIX)/$(PYTHON)
	PYTHON_LIBS := $(PYTHON_BASE_PREFIX)/libs/
	PYTHON_INCLUDES := $(PYTHON_BASE_PREFIX)/include/
else
    PYTHON_FOR_INSTALL_STEP := $(INSTALL_STEP_PREFIX)/bin/$(PYTHON)
	PYTHON_LIBS := $(PYTHON_BASE_PREFIX)/libs/python3.12/
	PYTHON_INCLUDES := $(PYTHON_BASE_PREFIX)/include/python3.12/
endif

OPTIMIZATION_FLAG=-O3
C_SOURCE=image_viewer/c_extensions
C_FLAGS_SHARED=-L$(PYTHON_LIBS) -I$(PYTHON_INCLUDES) -l$(PYTHON_DLL) $(OPTIMIZATION_FLAG) -march=native -mtune=native -ffinite-math-only -fgcse-las -fgcse-sm -fisolate-erroneous-paths-attribute -fno-signed-zeros -frename-registers -fsched-pressure -s -shared -Wall -Werror $(OS_FLAGS)

build-actions:
	gcc $(C_SOURCE)/actions/actions.c $(C_FLAGS_SHARED) -o image_viewer/actions/_actions.$(COMPILED_EXT)

build-image-read:
	gcc $(C_SOURCE)/image/read.c $(C_FLAGS_SHARED) -o image_viewer/image/_read.$(COMPILED_EXT) -lturbojpeg

build-util-generic:
	gcc $(C_SOURCE)/util/generic.c $(C_FLAGS_SHARED) -o image_viewer/util/_generic.$(COMPILED_EXT)

build-util-os-nt:
ifeq ($(OS),Windows_NT)
	gcc $(C_SOURCE)/util/os_nt.c $(C_SOURCE)/b64/cencode.c -I$(C_SOURCE) -lshlwapi -loleaut32 -lole32 $(C_FLAGS_SHARED) -o image_viewer/util/_os_nt.$(COMPILED_EXT)
endif

build-all: build-actions build-image-read build-util-generic build-util-os-nt

install:
	$(PYTHON_FOR_INSTALL_STEP) compile.py --assume-this-machine --strip --no-cleanup

validate:
	ruff check .
	ruff format --check
	mypy . --check-untyped-defs
	codespell

test:
	$(PYTHON_FOR_INSTALL_STEP) -m pytest -m "not memory_leak" --cov=image_viewer --cov-report term-missing

PYTHONUNBUFFERED=1
export PYTHONUNBUFFERED

test-memory-leak:
	$(PYTHON_FOR_INSTALL_STEP) -m pytest -m "memory_leak"
