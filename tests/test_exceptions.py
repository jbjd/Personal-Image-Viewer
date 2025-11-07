"""Tests for generic exception handling code."""

from unittest.mock import mock_open, patch

from image_viewer.exceptions import exception_hook


def test_exception_hook():
    """Should write exception to a file while swallowing errors."""

    exception = Exception("problem!")

    with patch("builtins.open", side_effect=OSError):
        # Should catch and not fail writing to file
        exception_hook(type(exception), exception, None, "")

    with patch("builtins.open", new_callable=mock_open) as mock_builtins_open:
        exception_hook(type(exception), exception, None, "")
        mock_builtins_open.assert_called_once_with("ERROR.log", "w", encoding="utf-8")
