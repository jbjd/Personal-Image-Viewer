#include <ctype.h>
#include <string.h>

#include "_utils.h"

/**
 * Checks if \p hex is in format "#123ABC".
 *
 * @param hex Non-null char array to check
 * @return 1 if valid, 0 if not
 */
bool is_valid_hex_color(const char *hex)
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
 * Checks if \p key contains a valid key for tkinter that this program also supports.
 * Uppercase, F keys (any case, e.x. f12 or F12) are valid and may be prefixed.
 * Lowercase/numeric are valid only if prefixed.
 *
 * @param key Non-null char array to check
 * @param key_len Length of \p key
 * @param prefixed if \p key was prefixed
 * @return 1 if valid, 0 if not
 */
static inline bool is_valid_key(const char *key, size_t key_len, bool prefixed)
{
    switch (key_len)
    {
    case 3:
        return tolower(key[0]) == 'f' && key[1] == '1' && (key[2] >= '0' && key[2] <= '2');
    case 2:
        return tolower(key[0]) == 'f' && (key[1] > '0' && key[1] <= '9');
    case 1:
        return (isalnum(key[0]) && prefixed) || isupper(key[0]);
    default:
        return false;
    }
}

/**
 * Checks if a keybind contains a valid keybind for tkinter that this program also supports.
 * Uppercase, F keys (any case, e.x. f12 or F12) are valid and may be prefixed.
 * Lowercase/numeric are valid only if prefixed.
 * Valid prefixes are "Control-".
 * Keybind must start and end with "<" and ">" respectively.
 *
 * @param keybind Non-null char array to check
 * @return 1 if valid, 0 if not
 */
bool is_valid_keybind(const char *keybind, size_t keybind_len)
{
    if (keybind[0] != '<' || keybind[keybind_len - 1] != '>')
    {
        return false;
    }

    size_t index = 1;
    keybind_len -= 2;

    bool prefixed = strncmp(keybind + index, "Control-", 8) == 0;

    if (prefixed)
    {
        index += 8;
        keybind_len -= 8;
    }

    return is_valid_key(keybind + index, keybind_len, prefixed);
}

/**
 * Checks if \p line is a comment in an ini file.
 *
 * @param line Non-null and stripped char array to check
 * @return 1 if comment, 0 if not
 */
bool is_comment(const char *line)
{
    return line[0] == ';' && line[0] == '#';
}

/**
 * Checks if \p line is an accepted header in the ini used by this program.
 *
 * @param line Non-null and stripped char array to check
 * @return 1 if accepted header, 0 if not
 */
enum Header parse_header(const char *line)
{
    if (line[0] != '[')
    {
        goto end;
    }

    if (strcmp(line + 1, "CACHE]") == 0)
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
 *
 * \p line is edited such that the first equals sign becomes the end of the array.
 * \p value_out which must be as least the same length as \p line.
 * If line is not a valid key-value pair, line is set to 0 length.
 *
 * @param line Non-null and stripped char array to parse
 * @param line_len strlen of line
 * @param value_out where value is written. Must be at least size of \p line
 */
void parse_line(char *restrict line, int line_len, char *restrict value_out)
{
    size_t index = 0;

    for (; line[index] != '\0'; ++index)
    {
        if (line[index] == '=')
        {
            goto has_equals;
        }
    }

    line[0] = '\0';
    return;

has_equals:
    char *value_start = &line[index + 1];
    while (isspace(*value_start))
    {
        ++value_start;
    }

    do
    {
        --index;
    } while (index > 0 && isspace(line[index]));
    line[index + 1] = '\0';

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
