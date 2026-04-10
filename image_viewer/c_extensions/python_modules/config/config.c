#define PY_SSIZE_T_CLEAN

#include <stddef.h>
#include <stdlib.h>

#include "../../c_optimizations.h"
#include "_utils.h"

#include "config.h"

#include <stdio.h> // tmp

// Config Start
static PyMemberDef Config_members[] = {
    {"font", Py_T_OBJECT_EX, offsetof(Config, font), Py_READONLY, 0},
    {"size", Py_T_OBJECT_EX, offsetof(Config, size), Py_READONLY, 0},
    {"copy_to_clipboard_as_base64", offsetof(Config, copy_to_clipboard_as_base64), Py_READONLY, 0},
    {"move_to_new_file", offsetof(Config, move_to_new_file), Py_READONLY, 0},
    {"optimize_image", offsetof(Config, optimize_image), Py_READONLY, 0},
    {"refresh", offsetof(Config, refresh), Py_READONLY, 0},
    {"reload_image", offsetof(Config, reload_image), Py_READONLY, 0},
    {"rename", offsetof(Config, rename), Py_READONLY, 0},
    {"show_details", offsetof(Config, show_details), Py_READONLY, 0},
    {"undo_most_recent_action", offsetof(Config, undo_most_recent_action), Py_READONLY, 0},
    {"background_color", offsetof(Config, background_color), Py_READONLY, 0},
    {NULL}};

static void Config_dealloc(Config *self)
{
    Py_DECREF(self->font);
    Py_DECREF(self->size);
    Py_DECREF(self->copy_to_clipboard_as_base64);
    Py_DECREF(self->move_to_new_file);
    Py_DECREF(self->optimize_image);
    Py_DECREF(self->refresh);
    Py_DECREF(self->reload_image);
    Py_DECREF(self->rename);
    Py_DECREF(self->show_details);
    Py_DECREF(self->undo_most_recent_action);
    Py_DECREF(self->background_color);
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
    config->font = NULL;
    config->size = NULL;
    config->copy_to_clipboard_as_base64 = NULL;
    config->move_to_new_file = NULL;
    config->optimize_image = NULL;
    config->refresh = NULL;
    config->reload_image = NULL;
    config->rename = NULL;
    config->show_details = NULL;
    config->undo_most_recent_action = NULL;
    config->background_color = NULL;

    return config;
}
// Config End

static void _update_config(Config *config, enum Header header, char *key, char *value)
{
    switch (header)
    {
    case CACHE:
        printf("asdf");
        // printf("%ld\n", PyLong_AsLong(PyLong_FromString("1a2", NULL, 10)));
        //   if (strcmp(key, "SIZE"))
        //   {
        //       config.size = strtol(value);
        //   }
        break;
    default:
        break;
    }
}

PyObject *parse_config_file()
{
    FILE *file = fopen("image_viewer/config.ini", "r");
    if (file == NULL)
    {
        goto check_defaults;
    }

    enum Header header = NONE;
    Config *config = Config_New();

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
            parse_line(line, line_len, LINE_MAX_SIZE, value);
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
    return 0;
}

static struct PyModuleDef config_module = {
    PyModuleDef_HEAD_INIT,
    "_config",
    NULL,
    -1,
    NULL};

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
