"""C extensions that aren't better classified in other files."""

def is_valid_hex_color(hex_color: str, /) -> bool:
    """Checks if a string is a valid hex color in the case-insensitive format '#ABC123'.

    :param hex_color: A possible hex color.
    :returns: True if hex_color is a valid color."""

def is_valid_keybind(keybind: str, /) -> bool:
    """Checks if a keybind is a valid subset of tkinter keybinds allowed in this program.

    :param keybind: A possible keybind.
    :returns: True if keybind follows one of the following regex:
    <F[0-9]> <F1[0-2]> <Control-[a-zA-Z0-9]>
    """
