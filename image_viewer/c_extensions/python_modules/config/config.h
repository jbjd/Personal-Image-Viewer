#ifndef PIV_CONFIG_CONFIG
#define PIV_CONFIG_CONFIG

#include <Python.h>

typedef struct
{
    PyObject_HEAD;
    // [FONT]
    PyObject *font; // str
    // [CACHE]
    PyObject *size; // int

    // [KEYBINDS]
    PyObject *keybing_config; // KeybindConfig

    // [UI]
    PyObject *background_color; // str
} Config;

typedef struct
{
    PyObject_HEAD;

    // [KEYBINDS]
    PyObject *copy_to_clipboard_as_base64; // str
    PyObject *move_to_new_file;            // str
    PyObject *optimize_image;              // str
    PyObject *refresh;                     // str
    PyObject *reload_image;                // str
    PyObject *rename;                      // str
    PyObject *show_details;                // str
    PyObject *undo_most_recent_action;     // str

} KeybindConfig;

#endif /* PIV_CONFIG_CONFIG */
