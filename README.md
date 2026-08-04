# Personal Image Viewer

A lightweight "Personal Image Viewer" written in Python 3.12

## Supported File Types

PNG, JPEG, WebP, AVIF, GIF, DDS

Animation support for PNG/WebP/GIF

## Description

An image viewer with the intent of being clean and simple; Images are fit to your screen in the best quality without
the clutter that other image viewers have.

Features Include:

* Optimized JPEG decoding with turbojpeg
* Rename/convert/delete images
* Undoing rename/convert/delete
* Drop via clipboard (Windows only)
* Exporting image as base64

Feel free to take this code and edit it however you like. Please don't use it for commercial purposes.

## Instructions To Get It Running

1. Have Python 3.12.x installed.

1. Install *libjpeg-turbo-official*.

1. Install *gcc* to compile \*.c into python module extensions and *make* to run Makefile commands.

1. Run 'make build-all' to build all \*.pyd/\*.so python module extensions.

1. Run 'pip install -r requirements.txt' to install python dependencies.

1. Run 'python main.py "C:/example/path/to/image.png"' to start the program.

## Instructions To Compile

1. Complete steps in [Instructions To Get It Running](#instructions-to-get-it-running)

1. Run 'pip install -r requirements_compile.txt' to install python dependencies for compilation. You will see warnings when compiling if the versions you are using are not what is expected. If you don't want to conflict with global installations of dependencies, use a virtual env.

1. With root privilege, run 'make install' (recommended) or 'python compile.py' if you want to set flags yourself, run 'python compile.py -h' to list all of them. This will compile the code and install it into the default location. You can edit the install path, and many other things, with various flags you can pass to compile.py.

### Instructions To Compile For Distribution

1. Run 'make build-all-dist'. This is the same as 'make build-all', without the *gcc* flags that enable optimizations for the current machine.

1. Run 'make bundle-dist' or 'make install-dist'. Bundle will install a distributable version of the program (includes licenses and no machine-specific Python or *gcc* optimizations) to the folder 'dist', while install while install it to the default location.

## Development

I am currently the only dev and tend to work on Windows. I have a Linux laptop that I periodically check things on, but due to this being a UI app, I can't cover everything with a unit test. Its possible I break Linux compatibility from time to time, so be warned.
