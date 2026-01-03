#include <stdbool.h>

#include <Python.h>

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

static inline bool is_valid_f_key(const char *keybind, Py_ssize_t len)
{
    switch (len)
    {
    case 3:
        return tolower(keybind[0]) == 'f' && keybind[1] == '1' && (keybind[2] >= '0' && keybind[2] <= '2');
    case 2:
        return tolower(keybind[0]) == 'f' && (keybind[1] > '0' && keybind[1] <= '9');
    default:
        return false;
    }
}

static inline bool is_valid_ctrl_key(const char *keybind, Py_ssize_t len)
{
    return len == 9 && 0 == strncmp(keybind, "Control-", 8) && (isalnum(keybind[8]));
}

static PyObject *is_valid_keybind(PyObject *self, PyObject *arg)
{
    Py_ssize_t size = PyUnicode_GetLength(arg);
    const Py_ssize_t MAX_POSSIBLE_SIZE = 11;

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

    return is_valid_f_key(keybind, size) || is_valid_ctrl_key(keybind, size) ? Py_True : Py_False;
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
