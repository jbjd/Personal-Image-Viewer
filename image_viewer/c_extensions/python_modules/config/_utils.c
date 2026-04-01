#include <ctype.h>
#include <string.h>

#include "_utils.h"

bool is_comment(const char *line)
{
    return line[0] == ';';
}

enum Header parse_header(const char *line, int line_len)
{
    if (line_len < 3 || line[0] != '[' || line[line_len - 1] != ']')
    {
        return NONE;
    }

    if (strcmp(line + 1, "FONT]") == 0)
    {
        return FONT;
    }
    else if (strcmp(line + 1, "CACHE]") == 0)
    {
        return CACHE;
    }
    else if (strcmp(line + 1, "KEYBINDS]") == 0)
    {
        return KEYBINDS;
    }
    else if (strcmp(line + 1, "UI]") == 0)
    {
        return UI;
    }

    return NONE;
}

char *str_strip(char *str)
{
    size_t size = strlen(str);

    if (size == 0)
    {
        goto end;
    }

    char *str_end = str + size - 1;
    while (str_end >= str && isspace(*str_end))
    {
        --str_end;
    }
    *(str_end + 1) = '\0';

    while (*str && isspace(*str))
    {
        ++str;
    }

end:
    return str;
}
