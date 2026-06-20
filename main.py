"""Entrypoint for the lightweight personal image viewer."""

import sys

if __name__ == "__main__" and len(sys.argv) > 1:
    if not __debug__:
        import os

        from image_viewer.exceptions import exception_hook

        os.chdir(os.path.dirname(sys.argv[0]))
        sys.excepthook = exception_hook

    from image_viewer.viewer import ViewerApp

    ViewerApp(sys.argv[1]).start()
