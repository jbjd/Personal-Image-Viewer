"""C functions exposed in python to help with testing."""

def is_valid_hex_color(hex_color: str, /) -> bool:
    """Checks if a string is a valid hex color in the case-insensitive format '#ABC123'.

    :param hex_color: A possible hex color.
    :returns: True if valid color."""

def is_valid_keybind(keybind: str, /) -> bool:
    """Checks if a keybind is an allowed and valid subset of tkinter keybinds.

    :param keybind: A possible keybind.
    :returns: True if keybind follows one of the following regex:
    <F[0-9]> <F1[0-2]> <Control-[a-zA-Z0-9]>
    """

def is_empty_or_valid_hex_color(hex_color: str, /) -> bool:
    """Checks if a string is empty or returns result of :func:`is_valid_hex_color`.
    Ignores quotes.

    :param hex_color: A possible hex color.
    :returns: True if empty or valid hex color."""

def is_empty_or_valid_keybind(keybind: str, /) -> bool:
    """Checks if a string is empty or return result of :func:`is_valid_keybind`.
    Ignores quotes.

    :param keybind: A possible keybind.
    :returns: True if valid keybind."""

def is_empty_or_valid_int(integer: str, /) -> bool:
    """Checks if a string is empty or a valid integer.
    Ignores quotes.

    :param integer: A possible integer.
    :returns: True if all numeric with optional sign."""
