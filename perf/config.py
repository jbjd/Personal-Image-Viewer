import string
import tempfile

from image_viewer._config import Config as CConfig
from image_viewer._config import parse_config_file
from perf._base import PerfTest
from perf._config import Config as PythonConfig


def _assert_configs(config_python: PythonConfig, c_config: CConfig) -> None:

    assert config_python.max_items_in_cache == c_config.cache_size

    assert (
        config_python.keybinds.copy_to_clipboard_as_base64
        == c_config.kb_copy_to_clipboard_as_base64
    )
    assert config_python.keybinds.move_to_new_file == c_config.kb_move_to_new_file
    assert config_python.keybinds.optimize_image == c_config.kb_optimize_image
    assert config_python.keybinds.refresh == c_config.kb_refresh
    assert config_python.keybinds.reload_image == c_config.kb_reload_image
    assert config_python.keybinds.rename == c_config.kb_rename
    assert config_python.keybinds.show_details == c_config.kb_show_details
    assert (
        config_python.keybinds.undo_most_recent_action
        == c_config.kb_undo_most_recent_action
    )

    assert config_python.background_color == c_config.ui_background_color
    assert config_python.font_file == c_config.ui_font


def run() -> None:
    perf_test = PerfTest(
        python_implementation=PythonConfig, c_implementation=parse_config_file
    )

    perf_test.run("Empty Config", 5, _assert_configs, "some bad path")
    perf_test.run("Default Config", 5, _assert_configs)

    with tempfile.NamedTemporaryFile("w") as tmp_file:
        for letter in string.ascii_lowercase:
            tmp_file.write(f"[{letter}]\n")
            for letter2 in string.ascii_lowercase:
                tmp_file.write(f"{letter2}=skdawuklvbaks3819fn389fb289bfukl\n")

        tmp_file.write("[UI]\n")
        tmp_file.write("FONT=iasvbweiruvbauios\n")

        perf_test.run("Big Junk Config", 5, _assert_configs, tmp_file.name)
