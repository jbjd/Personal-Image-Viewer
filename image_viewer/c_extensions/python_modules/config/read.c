#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static inline bool is_comment(const char *line)
{
    return line[0] == ';';
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

int main()
{
    FILE *file = fopen("image_viewer/config.ini", "r");
    if (file == NULL)
    {
        return 1;
    }

    const int LINE_MAX_SIZE = 512;
    char *raw_line = (char *)malloc(LINE_MAX_SIZE * sizeof(char));
    while (fgets(raw_line, LINE_MAX_SIZE, file))
    {
        char *line = str_strip(raw_line);
        size_t line_len = strlen(line);

        if (line_len == 0 || is_comment(line))
        {
            continue;
        }

        printf("%s\n", line);
    }

    fclose(file);
    free(raw_line);

    return 0;
}
