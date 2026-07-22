#define PY_SSIZE_T_CLEAN

#include "includes/config.h"

#include "includes/c_optimizations.h"
#include "includes/config_defaults.h"

#include <stddef.h>
#include <stdlib.h>

#define printf_err(...) fprintf(stderr, __VA_ARGS__)

// Config Start
static PyMemberDef Config_members[] = {
    {"cache_size", Py_T_OBJECT_EX, offsetof(Config, cache_size), Py_READONLY, 0},
    {"kb_copy_to_clipboard_as_base64", Py_T_OBJECT_EX, offsetof(Config, kb_copy_to_clipboard_as_base64), Py_READONLY, 0},
    {"kb_move_to_new_file", Py_T_OBJECT_EX, offsetof(Config, kb_move_to_new_file), Py_READONLY, 0},
    {"kb_optimize_image", Py_T_OBJECT_EX, offsetof(Config, kb_optimize_image), Py_READONLY, 0},
    {"kb_refresh", Py_T_OBJECT_EX, offsetof(Config, kb_refresh), Py_READONLY, 0},
    {"kb_reload_image", Py_T_OBJECT_EX, offsetof(Config, kb_reload_image), Py_READONLY, 0},
    {"kb_rename", Py_T_OBJECT_EX, offsetof(Config, kb_rename), Py_READONLY, 0},
    {"kb_show_details", Py_T_OBJECT_EX, offsetof(Config, kb_show_details), Py_READONLY, 0},
    {"kb_undo_most_recent_action", Py_T_OBJECT_EX, offsetof(Config, kb_undo_most_recent_action), Py_READONLY, 0},
    {"ui_background_color", Py_T_OBJECT_EX, offsetof(Config, ui_background_color), Py_READONLY, 0},
    {"ui_font", Py_T_OBJECT_EX, offsetof(Config, ui_font), Py_READONLY, 0},
    {NULL}
};

static void Config_dealloc(Config *self) {
    Py_DECREF(self->ui_font);
    Py_DECREF(self->cache_size);
    Py_DECREF(self->kb_copy_to_clipboard_as_base64);
    Py_DECREF(self->kb_move_to_new_file);
    Py_DECREF(self->kb_optimize_image);
    Py_DECREF(self->kb_refresh);
    Py_DECREF(self->kb_reload_image);
    Py_DECREF(self->kb_rename);
    Py_DECREF(self->kb_show_details);
    Py_DECREF(self->kb_undo_most_recent_action);
    Py_DECREF(self->ui_background_color);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject Config_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_config.Config",
    .tp_basicsize = sizeof(Config),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .tp_dealloc = (destructor)Config_dealloc,
    .tp_members = Config_members,
};

static inline Config *Config_New() {
    Config *config = (Config *)PyObject_New(Config, &Config_Type);
    config->ui_font = NULL;
    config->cache_size = NULL;
    config->kb_copy_to_clipboard_as_base64 = NULL;
    config->kb_move_to_new_file = NULL;
    config->kb_optimize_image = NULL;
    config->kb_refresh = NULL;
    config->kb_reload_image = NULL;
    config->kb_rename = NULL;
    config->kb_show_details = NULL;
    config->kb_undo_most_recent_action = NULL;
    config->ui_background_color = NULL;

    return config;
}

static void Config_SetDefaults(PyObject *self, Config *config) {
    if (config->cache_size == NULL) {
        config->cache_size = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_CACHE_SIZE));
    }
    if (config->kb_copy_to_clipboard_as_base64 == NULL) {
        config->kb_copy_to_clipboard_as_base64 = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64));
    }
    if (config->kb_move_to_new_file == NULL) {
        config->kb_move_to_new_file = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_MOVE_TO_NEW_FILE));
    }
    if (config->kb_optimize_image == NULL) {
        config->kb_optimize_image = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_OPTIMIZE_IMAGE));
    }
    if (config->kb_refresh == NULL) {
        config->kb_refresh = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_REFRESH));
    }
    if (config->kb_reload_image == NULL) {
        config->kb_reload_image = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_RELOAD_IMAGE));
    }
    if (config->kb_rename == NULL) {
        config->kb_rename = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_RENAME));
    }
    if (config->kb_show_details == NULL) {
        config->kb_show_details = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_SHOW_DETAILS));
    }
    if (config->kb_undo_most_recent_action == NULL) {
        config->kb_undo_most_recent_action = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_KB_UNDO_MOST_RECENT_ACTION));
    }
    if (config->ui_background_color == NULL) {
        config->ui_background_color = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_UI_BACKGROUND_COLOR));
    }
    if (config->ui_font == NULL) {
        config->ui_font = PyObject_GetAttrString(self, VARIABLE_NAME(DEFAULT_UI_FONT));
    }
}
// Config End

static void _print_err_unexpected_line(const char *line) {
    printf_err("Unexpected line: \"%s\"\n", line);
}

static void _print_err_bad_value(const char *restrict key, const char *restrict value, enum Section section, const char *restrict reason) {
    printf_err("Bad value for key \"%s\" value \"%s\" in section [%s]: %s\n", key, value, Section_to_string(section), reason);
}

static void _print_err_bad_key(const char *restrict key, const char *restrict value, enum Section section, const char *restrict reason) {
    printf_err("Bad key \"%s\" with value \"%s\" in section [%s]: %s\n", key, value, Section_to_string(section), reason);
}

// TODO: Error on empty value and print what default would be
static PyObject *Py_from_string_or_null(char *value) {
    return *value == '\0' ? NULL : PyUnicode_FromString(value);
}

static PyObject *Py_from_string_or_null_with_validation(char *value, bool (*validator)(const char *), bool *valid_out) {
    if (*value == '\0') {
        *valid_out = true;
        return NULL;
    }

    *valid_out = validator(value);
    if (!(*valid_out)) {
        return NULL;
    }

    return PyUnicode_FromString(value);
}

static PyObject *Py_from_int_or_null(char *value, int *error_out) {
    if (*value == '\0') {
        return NULL;
    }
    return PyLong_FromLong(str_to_int(value, 0, 100, DEFAULT_CACHE_SIZE, error_out));
}

static inline void _update_config(Config *config, enum Section section, char *restrict key, char *restrict value, bool validate) {
    PyObject **target = NULL;
    PyObject *Py_value = NULL;

    switch (section) {
    case CACHE:
        if (strcmp(key, "SIZE") == 0) {
            int error;
            target = &config->cache_size;
            Py_value = Py_from_int_or_null(value, &error);
            if (validate && error) {
                _print_err_bad_value(key, value, section, "Not an interger in range 0-100");
            }
        }
        break;
    case KEYBINDS:

        if (strcmp(key, "COPY_TO_CLIPBOARD_AS_BASE64") == 0) {
            target = &config->kb_copy_to_clipboard_as_base64;
        } else if (strcmp(key, "MOVE_TO_NEW_FILE") == 0) {
            target = &config->kb_move_to_new_file;
        } else if (strcmp(key, "OPTIMIZE_IMAGE") == 0) {
            target = &config->kb_optimize_image;
        } else if (strcmp(key, "REFRESH") == 0) {
            target = &config->kb_refresh;
        } else if (strcmp(key, "RELOAD_IMAGE") == 0) {
            target = &config->kb_reload_image;
        } else if (strcmp(key, "RENAME") == 0) {
            target = &config->kb_rename;
        } else if (strcmp(key, "SHOW_DETAILS") == 0) {
            target = &config->kb_show_details;
        } else if (strcmp(key, "UNDO_MOST_RECENT_ACTION") == 0) {
            target = &config->kb_undo_most_recent_action;
        }

        if (target != NULL) {
            bool valid;
            Py_value = Py_from_string_or_null_with_validation(value, is_valid_keybind, &valid);
            if (validate && !valid) {
                _print_err_bad_value(key, value, section, "Not a valid keybind");
            }
        }

        break;
    case UI:
        if (strcmp(key, "BACKGROUND_COLOR") == 0) {
            target = &config->ui_background_color;
            bool valid;
            Py_value = Py_from_string_or_null_with_validation(value, is_valid_hex_color, &valid);
            if (validate && !valid) {
                _print_err_bad_value(key, value, section, "Not a valid hex color");
            }
        } else if (strcmp(key, "FONT") == 0) {
            target = &config->ui_font;
            Py_value = Py_from_string_or_null(value);
        }
        break;
    case UNKNOWN:
        break;
    }

    if (target != NULL) {
        if (validate) {
            if (*target != NULL) {
                _print_err_bad_key(key, value, section, "Duplicate");
            }
            Py_XDECREF(Py_value);
            *target = Py_None; // Set to something since real value does not matter
        } else {
            *target = Py_value;
        }
    } else if (validate) {
        _print_err_bad_key(key, value, section, "Unknown");
    }
}

static inline void _parse_file_into_config(FILE *file, Config *config, bool validate) {
    enum Section section = UNKNOWN;

    char *raw_line = (char *)malloc(LINE_MAX_SIZE * sizeof(char));
    while (fgets(raw_line, LINE_MAX_SIZE, file)) {
        char *line = str_strip(raw_line);

        if (should_ignore_line(line)) {
            continue;
        }

        size_t line_size = strlen(line);

        if (is_section(line, line_size)) {
            section = parse_section(line + 1, line_size - 2);
            if (validate && section == UNKNOWN) {
                printf_err("Unknown section: %s\n", line);
            }
            continue;
        }

        if (section != UNKNOWN) {
            char value[LINE_MAX_SIZE];
            bool success = parse_line(line, line_size, value);
            if (!success && validate) {
                _print_err_unexpected_line(line);
            } else if (*value != '\0' || validate) {
                _update_config(config, section, line, value, validate);
            }
        } else if (validate) {
            _print_err_unexpected_line(line);
        }
    }
    free(raw_line);
}

PyObject *parse_config_file(PyObject *self, PyObject *args) {
    char *path = NULL;
    if (unlikely(!PyArg_ParseTuple(args, "|s", &path))) {
        return NULL;
    }

    Config *config = Config_New();

    FILE *file = fopen(path == NULL ? "image_viewer/config.ini" : path, "r");
    if (file == NULL) {
        goto check_defaults;
    }

    _parse_file_into_config(file, config, false);
    fclose(file);

check_defaults:
    Config_SetDefaults(self, config);
    return (PyObject *)config;
}

static void _print_err_missing_key(const char *key, enum Section section) {
    printf_err("Missing key \"%s\" in section [%s]\n", key, Section_to_string(section));
}

static void _print_err_missing_keys(Config *config) {
    if (config->cache_size == NULL) {
        _print_err_missing_key("cache_size", CACHE);
    }
    if (config->kb_copy_to_clipboard_as_base64 == NULL) {
        _print_err_missing_key("kb_copy_to_clipboard_as_base64", KEYBINDS);
    }
    if (config->kb_move_to_new_file == NULL) {
        _print_err_missing_key("kb_move_to_new_file", KEYBINDS);
    }
    if (config->kb_optimize_image == NULL) {
        _print_err_missing_key("kb_optimize_image", KEYBINDS);
    }
    if (config->kb_refresh == NULL) {
        _print_err_missing_key("kb_refresh", KEYBINDS);
    }
    if (config->kb_reload_image == NULL) {
        _print_err_missing_key("kb_reload_image", KEYBINDS);
    }
    if (config->kb_rename == NULL) {
        _print_err_missing_key("kb_rename", KEYBINDS);
    }
    if (config->kb_show_details == NULL) {
        _print_err_missing_key("kb_show_details", KEYBINDS);
    }
    if (config->kb_undo_most_recent_action == NULL) {
        _print_err_missing_key("kb_undo_most_recent_action", KEYBINDS);
    }
    if (config->ui_background_color == NULL) {
        _print_err_missing_key("ui_background_color", UI);
    }
    if (config->ui_font == NULL) {
        _print_err_missing_key("ui_font", UI);
    }
}

PyObject *validate_config_file(PyObject *self, PyObject *arg) {
    const char *path = PyUnicode_AsUTF8(arg);

    FILE *file = fopen(path, "r");
    if (file == NULL) {
        PyErr_SetNone(PyExc_FileNotFoundError);
        return NULL;
    }

    Config *config = Config_New();
    _parse_file_into_config(file, config, true);
    fclose(file);

    _print_err_missing_keys(config);

    return Py_None;
}

static PyMethodDef config_methods[] = {
    {"parse_config_file", (PyCFunction)parse_config_file, METH_VARARGS, NULL},
    {"validate_config_file", validate_config_file, METH_O, NULL},
    {NULL, NULL, 0, NULL}
};

static int config_exec(PyObject *module) {
    if (unlikely(
            PyType_Ready(&Config_Type) ||
            PyModule_AddObjectRef(module, VARIABLE_NAME(Config), (PyObject *)&Config_Type) ||
            PyModule_AddIntConstant(module, VARIABLE_NAME(DEFAULT_CACHE_SIZE), DEFAULT_CACHE_SIZE) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64), DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_MOVE_TO_NEW_FILE), DEFAULT_KB_MOVE_TO_NEW_FILE) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_OPTIMIZE_IMAGE), DEFAULT_KB_OPTIMIZE_IMAGE) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_REFRESH), DEFAULT_KB_REFRESH) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_RELOAD_IMAGE), DEFAULT_KB_RELOAD_IMAGE) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_RENAME), DEFAULT_KB_RENAME) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_SHOW_DETAILS), DEFAULT_KB_SHOW_DETAILS) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_KB_UNDO_MOST_RECENT_ACTION), DEFAULT_KB_UNDO_MOST_RECENT_ACTION) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_UI_BACKGROUND_COLOR), DEFAULT_UI_BACKGROUND_COLOR) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DEFAULT_UI_FONT), DEFAULT_UI_FONT)
        )) {
        Py_DECREF(module);
        return -1;
    }

    return 0;
}

static PyModuleDef_Slot config_slots[] = {
    {Py_mod_exec, config_exec},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static struct PyModuleDef config_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_config",
    .m_size = 0,
    .m_methods = config_methods,
    .m_slots = config_slots
};

PyMODINIT_FUNC PyInit__config(void) {
    return PyModuleDef_Init(&config_module);
}
