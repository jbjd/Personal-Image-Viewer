"""Entrypoint for the lightweight personal image viewer."""

import sys

if __name__ == "__main__" and len(sys.argv) > 1:
    from image_viewer.viewer import ViewerApp

    ViewerApp().start()
