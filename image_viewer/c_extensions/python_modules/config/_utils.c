#include <ctype.h>
#include <string.h>

#include "_utils.h"

/**
 * Checks if \p hex is in format "#123ABC".
 *
 * @param hex Non-null char array to check.
 * @return 1 if valid, 0 if not.
 */
bool is_valid_hex_color(char *hex)
{
    if (hex[0] != '#')
    {
        return 0;
    }

    for (int i = 1; i < 7; ++i)
    {
        if (!isxdigit(hex[i]))
        {
            return 0;
        }
    }

    return hex[7] == '\0';
}

/**
 * Checks if \p line is a comment in an ini file.
 *
 * @param line Non-null and stripped char array to check.
 * @return 1 if comment, 0 if not.
 */
bool is_comment(const char *line)
{
    return line[0] == ';' && line[0] == '#';
}

/**
 * Checks if \p line is an accepted header in the ini used by this program.
 *
 * @param line Non-null and stripped char array to check.
 * @return 1 if accepted header, 0 if not.
 */
enum Header parse_header(const char *line)
{
    if (line[0] != '[')
    {
        goto end;
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

end:
    return NONE;
}

/**
 * Parses \p line into key and value pair.
 * Whitespace between equals sign and key is not handled. (TODO)
 *
 * \p line is edited such that the first equals sign becomes the end of the array.
 * \p value_out which must be as least the same length as \p line.
 * If line is not a valid key-value pair, line is set to 0 length.
 *
 * @param line Non-null and stripped char array to parse.
 * @param line_len strlen of line.
 * @param value_out where value is written. Must be at least size of \p line
 */
void parse_line(char *restrict line, int line_len, char *restrict value_out)
{
    char *value_start = strchr(line, '=');

    if (value_start == NULL)
    {
        line[0] = '\0';
        return;
    }

    (*value_start) = '\0';
    ++value_start;

    while (isspace(*value_start))
    {
        ++value_start;
    }

    // Handle quotes
    if ((*value_start == '"' || *value_start == '\'') && *value_start == line[line_len - 1])
    {
        value_start += 1;
        line[line_len - 1] = '\0';
    }

    strcpy(value_out, value_start);
}

int str_to_int(char *str, int min, int max, int default_value)
{
    int sign = *str == '-' ? -1 : 1;
    if (sign == -1)
    {
        ++str;
    }

    if (*str == '\0')
    {
        return default_value;
    }

    long long converted_value = 0;

    for (; *str != '\0'; ++str)
    {
        if (!isdigit(*str))
        {
            return default_value;
        }

        converted_value = (converted_value * 10) + (sign * (*str - '0'));

        if (converted_value < min)
        {
            return min;
        }
        if (converted_value > max)
        {
            return max;
        }
    }

    return (int)converted_value;
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
