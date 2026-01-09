#include <stdbool.h>

#include <Python.h>

/**
 * Checks if input is a valid hex string in format #123ABC.
 *
 * @param self Instance of this module.
 * @param arg A PyUnicode string to check.
 * @return PyBool if valid.
 */
static PyObject *is_valid_hex_color(PyObject *self, PyObject *arg)
{
    const ssize_t hexLen = PyUnicode_GetLength(arg);

    if (hexLen != 7)
    {
        return Py_False;
    }

    const char *hex = PyUnicode_AsUTF8(arg);

    if (hex[0] != '#')
    {
        return Py_False;
    }

    for (int i = 1; i < 7; ++i)
    {
        if (!isxdigit(hex[i]))
        {
            return Py_False;
        }
    }

    return Py_True;
}

/**
 * Checks if a key contains a valid key for tkinter that this program also supports.
 * Uppercase, F keys (any case, e.x. f12 or F12) are valid and may be prefixed.
 * Lowercase/numeric are valid only if prefixed.
 *
 * @param key A string to check.
 * @param len Length of @p key.
 * @return bool if valid.
 */
static inline bool is_valid_key(const char *key, Py_ssize_t len, bool prefixed)
{
    switch (len)
    {
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
 * @param self Instance of this module.
 * @param arg A PyUnicode string to check.
 * @return PyBool if valid.
 */
static PyObject *is_valid_keybind(PyObject *self, PyObject *arg)
{
    Py_ssize_t size = PyUnicode_GetLength(arg);
    const Py_ssize_t MAX_POSSIBLE_SIZE = 13;

    if (size < 3 || size > MAX_POSSIBLE_SIZE)
    {
        return Py_False;
    }

    const char *keybind = PyUnicode_AsUTF8(arg);

    if (keybind[0] != '<' || keybind[size - 1] != '>')
    {
        return Py_False;
    }

    keybind += 1;
    size -= 2;

    bool prefixed = strncmp(keybind, "Control-", 8) == 0;

    if (prefixed)
    {
        keybind += 8;
        size -= 8;
    }

    return is_valid_key(keybind, size, prefixed) ? Py_True : Py_False;
}

static PyMethodDef generic_methods[] = {
    {"is_valid_hex_color", is_valid_hex_color, METH_O, NULL},
    {"is_valid_keybind", is_valid_keybind, METH_O, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef generic_module = {
    PyModuleDef_HEAD_INIT,
    "_generic",
    NULL,
    -1,
    generic_methods};

PyMODINIT_FUNC PyInit__generic(void)
{
    return PyModule_Create(&generic_module);
}
