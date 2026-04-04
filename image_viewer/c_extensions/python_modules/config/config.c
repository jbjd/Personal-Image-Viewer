#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "_utils.h"

#include "config.h"

static void update_config(Config *config, enum Header header, char *key, void *value)
{
    switch (header)
    {
    case CACHE:
        break;
    default:
        break;
    }
}

int main()
{
    FILE *file = fopen("image_viewer/config.ini", "r");
    if (file == NULL)
    {
        return 1;
    }

    enum Header header = NONE;
    Config config = {.size = 20};

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

        enum Header new_header = parse_header(line);
        if (new_header != NONE)
        {
            header = new_header;
        }
        else if (header != NONE)
        {
            char value[LINE_MAX_SIZE];
            parse_line(line, line_len, LINE_MAX_SIZE, value);
            if (value[0] != '\0')
            {
                printf("Key: %s Value: %s\n", line, value);
            }
        }
        // else is value without header, ignore
    }

    fclose(file);
    free(raw_line);

    return 0;
}
