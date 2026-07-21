#include "includes/config.h"

#include <ctype.h>
#include <string.h>

const int LINE_MAX_SIZE = 512;

char *Section_to_string(enum Section section) {
    switch (section) {
    case CACHE:
        return "CACHE";
    case KEYBINDS:
        return "KEYBINDS";
    case UI:
        return "UI";
    default:
        return "Unknown";
    }
}

/**
 * Checks if `hex` is in format "#123ABC".
 *
 * @param hex Non-null char array to check
 * @return 1 if valid, 0 if not
 */
bool is_valid_hex_color(const char *hex) {
    if (hex[0] != '#') {
        return 0;
    }

    for (int i = 1; i < 7; ++i) {
        if (!isxdigit(hex[i])) {
            return 0;
        }
    }

    return hex[7] == '\0';
}

/**
 * Checks if `key` contains a valid key for tkinter that this program also supports.
 * Uppercase, F keys (any case, e.x. f12 or F12) are valid and may be prefixed.
 * Lowercase/numeric are valid only if prefixed.
 *
 * @param key Non-null char array to check
 * @param key_len Length of `key`
 * @param prefixed if `key` was prefixed
 * @return 1 if valid, 0 if not
 */
static inline bool is_valid_key(const char *key, size_t key_len, bool prefixed) {
    switch (key_len) {
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
bool is_valid_keybind(const char *keybind, size_t keybind_len) {
    if (keybind[0] != '<' || keybind[keybind_len - 1] != '>') {
        return false;
    }

    size_t index = 1;
    keybind_len -= 2;

    bool prefixed = strncmp(keybind + index, "Control-", 8) == 0;

    if (prefixed) {
        index += 8;
        keybind_len -= 8;
    }

    return is_valid_key(keybind + index, keybind_len, prefixed);
}

/**
 * Strips whitespace from start and end of string.
 *
 * @param str Non-null string to strip
 * @return updated pointer to the same string
 */
char *str_strip(char *str) {
    size_t size = strlen(str);

    if (size == 0) {
        goto end;
    }

    char *str_end = str + size - 1;
    while (str_end >= str && isspace(*str_end)) {
        --str_end;
    }
    *(str_end + 1) = '\0';

    while (*str && isspace(*str)) {
        ++str;
    }

end:
    return str;
}

/**
 * Checks if `line` is a comment in an ini file or if line is empty.
 *
 * @param line Non-null and stripped char array to check
 * @return 1 if comment, 0 if not
 */
bool should_ignore_line(const char *line) {
    return line[0] == '\0' || line[0] == ';' || line[0] == '#';
}

/**
 * Checks if `line` is contains a section value.
 *
 * @param line Non-null and stripped char array to check
 * @param line_size size of `line` input
 * @return 1 if accepted section, 0 if not
 */
inline bool is_section(const char *line, size_t line_size) {
    return line[0] == '[' && line[line_size - 1] == ']';
}

/**
 * Checks if `line` is an accepted section in the ini used by this program.
 * Assumes the brackets have been removed.
 *
 * @param line Non-null and stripped char array to check
 * @param line_size size of `line` input
 * @return Header enum containing accepted value or Unknown
 */
enum Section parse_section(const char *line, size_t line_size)
{
    switch (line_size) {
    case 2:
        if (memcmp(line, "UI", 2) == 0) {
            return UI;
        }
    case 5:
        if (memcmp(line, "CACHE", 5) == 0) {
            return CACHE;
        }
    case 8:
        if (memcmp(line, "KEYBINDS", 8) == 0) {
            return KEYBINDS;
        }
    }

    return UNKNOWN;
}

/**
 * Parses `line` into key and value pair.
 *
 * `line` is edited such that the first equals sign becomes the end of the array.
 * `value_out` which must be as least the same length as `line`.
 * If line is not a valid key-value pair, line is set to 0 length.
 *
 * @param line Non-null and stripped char array to parse
 * @param line_size strlen of line
 * @param value_out where value is written. Must be at least size of `line`
 */
void parse_line(char *restrict line, int line_size, char *restrict value_out) {
    size_t index = 0;

    for (; line[index] != '\0'; ++index) {
        if (line[index] == '=') {
            goto has_equals;
        }
    }

    line[0] = '\0';
    return;

has_equals:
    size_t value_start = index + 1;
    while (isspace(line[value_start])) {
        ++value_start;
    }

    do {
        --index;
    } while (index > 0 && isspace(line[index]));
    line[index + 1] = '\0';

    // Handle quotes
    if ((line[value_start] == '"' || line[value_start] == '\'') && line[value_start] == line[line_size - 1]) {
        ++value_start;
        line[line_size - 1] = '\0';
    }

    memcpy(value_out, line + value_start, line_size - value_start + 1);
}

/**
 * Custom string to int parse with clamps and negative handling. Invalid values return default.
 *
 * @param str Non-null string to parse
 * @param min Minimum value returned
 * @param max Maximum value returned
 * @param default_value Returned when non-integer formatted value passed
 * @param error_out Set to 0 if value is within min/max, 1 if not or contains invalid values
 * @return parsed value as int
 */
int str_to_int(char *str, int min, int max, int default_value, int *error_out) {
    int sign;
    if (*str == '-') {
        sign = -1;
        ++str;
    } else {
        sign = 1;
    }

    if (*str == '\0') {
        *error_out = 1;
        return default_value;
    }

    long long converted_value = 0;

    for (; *str != '\0'; ++str) {
        if (!isdigit(*str)) {
            *error_out = 1;
            return default_value;
        }

        converted_value = (converted_value * 10) + (sign * (*str - '0'));

        if (converted_value < min) {
            *error_out = 1;
            return min;
        }
        if (converted_value > max) {
            *error_out = 1;
            return max;
        }
    }

    *error_out = 0;
    return (int)converted_value;
}
