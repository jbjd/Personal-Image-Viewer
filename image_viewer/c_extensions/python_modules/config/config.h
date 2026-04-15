#ifndef PIV_CONFIG_CONFIG
#define PIV_CONFIG_CONFIG

#include <Python.h>

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

#endif /* PIV_CONFIG_CONFIG */
