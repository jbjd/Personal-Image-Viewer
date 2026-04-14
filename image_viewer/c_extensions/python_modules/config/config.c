#define PY_SSIZE_T_CLEAN

#include <stddef.h>
#include <stdlib.h>

#include "../../c_optimizations.h"
#include "_utils.h"

#include "config.h"

#include <stdio.h> // tmp

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
    {NULL}};

static void Config_dealloc(Config *self)
{
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

static inline Config *Config_New()
{
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

const int DEFAULT_CACHE_SIZE = 20;

static inline void Config_SetDefaults(Config *config)
{
    if (config->cache_size == NULL)
    {
        config->cache_size = PyLong_FromLong(DEFAULT_CACHE_SIZE);
    }
    if (config->kb_copy_to_clipboard_as_base64 == NULL)
    {
        config->kb_copy_to_clipboard_as_base64 = PyUnicode_FromString("<Control-E>");
    }
    if (config->kb_move_to_new_file == NULL)
    {
        config->kb_move_to_new_file = PyUnicode_FromString("<Control-m>");
    }
    if (config->kb_optimize_image == NULL)
    {
        config->kb_optimize_image = PyUnicode_FromString("<Control-o>");
    }
    if (config->kb_refresh == NULL)
    {
        config->kb_refresh = PyUnicode_FromString("<Control-r>");
    }
    if (config->kb_reload_image == NULL)
    {
        config->kb_reload_image = PyUnicode_FromString("<F5>");
    }
    if (config->kb_rename == NULL)
    {
        config->kb_rename = PyUnicode_FromString("<F2>");
    }
    if (config->kb_show_details == NULL)
    {
        config->kb_show_details = PyUnicode_FromString("<Control-d>");
    }
    if (config->kb_undo_most_recent_action == NULL)
    {
        config->kb_undo_most_recent_action = PyUnicode_FromString("<Control-z>");
    }
    if (config->ui_background_color == NULL)
    {
        config->ui_background_color = PyUnicode_FromString("#000000");
    }
    if (config->ui_font == NULL)
    {
#if defined(__WIN32__)
        char *font = "arial.ttf";
#else
        char *font = "LiberationSans-Regular.ttf";
#endif
        config->ui_font = PyUnicode_FromString(font);
    }
}
// Config End

static void _update_config(Config *config, enum Header header, char *key, char *value)
{
    switch (header)
    {
    case CACHE:
        if (strcmp(key, "SIZE") == 0)
        {
            config->cache_size = PyLong_FromLong(str_to_int(value, 0, 100, DEFAULT_CACHE_SIZE));
        }
    case KEYBINDS:
        if (!is_valid_keybind(value, strlen(value)))
        {
            break;
        }
        if (strcmp(key, "COPY_TO_CLIPBOARD_AS_BASE64") == 0)
        {
            config->kb_copy_to_clipboard_as_base64 = PyUnicode_FromString(value);
        }
        if (strcmp(key, "MOVE_TO_NEW_FILE") == 0)
        {
            config->kb_move_to_new_file = PyUnicode_FromString(value);
        }
        if (strcmp(key, "OPTIMIZE_IMAGE") == 0)
        {
            config->kb_optimize_image = PyUnicode_FromString(value);
        }
        if (strcmp(key, "REFRESH") == 0)
        {
            config->kb_refresh = PyUnicode_FromString(value);
        }
        if (strcmp(key, "RELOAD_IMAGE") == 0)
        {
            config->kb_reload_image = PyUnicode_FromString(value);
        }
        if (strcmp(key, "RENAME") == 0)
        {
            config->kb_rename = PyUnicode_FromString(value);
        }
        if (strcmp(key, "SHOW_DETAILS") == 0)
        {
            config->kb_show_details = PyUnicode_FromString(value);
        }
        if (strcmp(key, "UNDO_MOST_RECENT_ACTION") == 0)
        {
            config->kb_undo_most_recent_action = PyUnicode_FromString(value);
        }
        break;
    case UI:
        if (strcmp(key, "BACKGROUND_COLOR") == 0 && is_valid_hex_color(value))
        {
            config->ui_background_color = PyUnicode_FromString(value);
        }
        else if (strcmp(key, "FONT") == 0)
        {
            config->ui_font = PyUnicode_FromString(value);
        }
        break;
    default:
        break;
    }
}

PyObject *parse_config_file()
{
    Config *config = Config_New();

    FILE *file = fopen("image_viewer/config.ini", "r");
    if (file == NULL)
    {
        goto check_defaults;
    }

    enum Header header = NONE;

    const int LINE_MAX_SIZE = 512;
    char *raw_line = (char *)malloc(LINE_MAX_SIZE * sizeof(char));
    while (fgets(raw_line, LINE_MAX_SIZE, file))
    {
        char *line = str_strip(raw_line);
        size_t line_len = strlen(line);

        if (line_len < 3 || is_comment(line))
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
            parse_line(line, line_len, value);
            if (value[0] != '\0')
            {
                _update_config(config, header, line, value);
            }
        }
        // else is value without header, ignore
    }

    fclose(file);
    free(raw_line);

check_defaults:
    Config_SetDefaults(config);
    return (PyObject *)config;
}

static PyMethodDef config_methods[] = {
    {"parse_config_file", (PyCFunction)parse_config_file, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef config_module = {
    PyModuleDef_HEAD_INIT,
    "_config",
    NULL,
    -1,
    config_methods};

PyMODINIT_FUNC PyInit__config(void)
{
    if (unlikely(PyType_Ready(&Config_Type) < 0))
    {
        return NULL;
    }

    PyObject *module = PyModule_Create(&config_module);

    if (unlikely(PyModule_AddObjectRef(module, "Config", (PyObject *)&Config_Type) < 0))
    {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
