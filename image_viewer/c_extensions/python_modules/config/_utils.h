#ifndef PIV_CONFIG_UTILS
#define PIV_CONFIG_UTILS

#include <Python.h>

enum Header
{
    NONE,
    FONT,
    CACHE,
    KEYBINDS,
    UI,
};

bool is_valid_hex_color(char *hex);

bool is_valid_keybind(char *keybind, size_t keybind_len);

bool is_comment(const char *line);

enum Header parse_header(const char *line);

void parse_line(char *restrict line, int line_len, char *restrict value_out);

int str_to_int(char *str, int min, int max, int default_value);

char *str_strip(char *str);

#endif /* PIV_CONFIG_UTILS */
