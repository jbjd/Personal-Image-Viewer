"""Entrypoint for the lightweight personal image viewer."""

import sys

if __name__ == "__main__" and len(sys.argv) > 1:
    from image_viewer.exceptions import exception_hook
    from image_viewer.viewer import ViewerApp

    if not __debug__:
        import os

        os.chdir(os.path.dirname(sys.argv[0]))
        sys.excepthook = exception_hook

    if os.name == "nt":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    ViewerApp(sys.argv[1]).start()
