#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "_utils.h"

int main()
{
    FILE *file = fopen("image_viewer/config.ini", "r");
    if (file == NULL)
    {
        return 1;
    }

    enum Header header = NONE;

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

        enum Header new_header = parse_header(line, line_len);
        if (new_header != NONE)
        {
            header = new_header;
        }
        else if (header != NONE)
        {
            const char *tmp[] = {
                "NONE",
                "FONT",
                "CACHE",
                "KEYBINDS",
                "UI",
            };
            printf("Header %s - %s\n", tmp[header], line);
        }
        // else is value without header, ignore
    }

    fclose(file);
    free(raw_line);

    return 0;
}
