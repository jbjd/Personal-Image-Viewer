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

bool is_comment(const char *line);

enum Header parse_header(const char *line);

void parse_line(char *__restrict__ line, int line_len, int value_len, char *__restrict__ value_out);

// int str_to_int(char *str, int min, int max, int default);

char *str_strip(char *str);

#endif /* PIV_CONFIG_UTILS */
