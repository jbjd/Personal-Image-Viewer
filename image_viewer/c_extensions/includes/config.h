#ifndef PIV_CONFIG
#define PIV_CONFIG

#include <Python.h>
#include <stdbool.h>

enum Header
{
    NONE,
    CACHE,
    KEYBINDS,
    UI,
};

typedef struct
{
    PyObject_HEAD;

    // [CACHE]
    PyObject *cache_size; // int

    // [KEYBINDS]
    PyObject *kb_copy_to_clipboard_as_base64; // str
    PyObject *kb_move_to_new_file;            // str
    PyObject *kb_optimize_image;              // str
    PyObject *kb_refresh;                     // str
    PyObject *kb_reload_image;                // str
    PyObject *kb_rename;                      // str
    PyObject *kb_show_details;                // str
    PyObject *kb_undo_most_recent_action;     // str

    // [UI]
    PyObject *ui_background_color; // str
    PyObject *ui_font;             // str
} Config;

extern const int LINE_MAX_SIZE;

bool is_valid_hex_color(const char *hex);

bool is_valid_keybind(const char *keybind, size_t keybind_len);

bool is_comment(const char *line);

enum Header parse_header(const char *line);

void parse_line(char *restrict line, int line_len, char *restrict value_out);

int str_to_int(char *str, int min, int max, int default_value);

char *str_strip(char *str);

#endif /* PIV_CONFIG */
