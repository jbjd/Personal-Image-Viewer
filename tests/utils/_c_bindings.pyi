"""C functions exposed in python to help with testing."""

def is_valid_hex_color(hex_color: str, /) -> bool:
    """Checks if a string is a valid hex color in the case-insensitive format '#ABC123'.

    :param hex_color: A possible hex color
    :returns: True if valid color"""

def is_valid_keybind(keybind: str, /) -> bool:
    """Checks if a keybind is an allowed and valid subset of tkinter keybinds.

    :param keybind: A possible keybind
    :returns: True if keybind follows one of the following regex:
    <F[0-9]> <F1[0-2]> <Control-[a-zA-Z0-9]>
    """

def base64_encode(to_encode: str, /) -> str:
    """base64 encodes the input string.

    :param to_encode: A string to encode
    :returns: New base64 encoded version of the string"""
