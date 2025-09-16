"""Entrypoint for the lightweight personal image viewer."""

import sys

if __name__ == "__main__" and len(sys.argv) > 1:  # pragma: no cover
    from image_viewer.exception import exception_hook
    from image_viewer.util.os import get_path_to_exe_folder
    from image_viewer.viewer import ViewerApp

    path_to_exe_folder: str = get_path_to_exe_folder()

    if not __debug__:
        sys.excepthook = lambda error_type, error, trace: exception_hook(
            error_type, error, trace, path_to_exe_folder
        )

    ViewerApp(sys.argv[1], path_to_exe_folder).start()
