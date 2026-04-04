#include <ctype.h>
#include <string.h>

#include "_utils.h"

bool is_comment(const char *line)
{
    return line[0] == ';';
}

enum Header parse_header(const char *line)
{
    if (line[0] != '[')
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

void parse_line(char *__restrict__ line, int line_len, int value_len, char *__restrict__ value_out)
{
    char *value_start = strchr(line, '=');

    if (value_start == NULL)
    {
        line[0] = '\0';
        return;
    }

    (*value_start) = '\0';
    value_start += 1;

    size_t size_reduction = strlen(line) + 1;

    // Handle quotes
    if ((*value_start == '"' || *value_start == '\'') && *value_start == line[line_len - 1])
    {
        value_start += 1;
        line[line_len - 1] = '\0';
    }

    strncpy(value_out, value_start, value_len);
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
