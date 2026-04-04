#ifndef PIV_CONFIG_UTILS
#define PIV_CONFIG_UTILS

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

void parse_line(char *line, int line_len, int max_len, char *value_out);

char *str_strip(char *str);

#endif /* PIV_CONFIG_UTILS */
