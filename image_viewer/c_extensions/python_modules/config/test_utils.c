#include <Python.h>

#include "_utils.h"

/**
 * Wraps is_valid_hex_color so it can be called in Python.
 *
 * @param self Instance of this module.
 * @param arg A PyUnicode string to check.
 * @return PyBool if valid.
 */
static PyObject *Py_is_valid_hex_color(PyObject *self, PyObject *arg)
{
    Py_ssize_t size;
    const char *hex = PyUnicode_AsUTF8AndSize(arg, &size);

    if (size == -1)
    {
        return NULL;
    }

    return PyBool_FromLong(is_valid_hex_color(hex));
}

/**
 * Wraps is_valid_keybind so it can be called in Python.
 *
 * @param self Instance of this module.
 * @param arg A PyUnicode string to check.
 * @return PyBool if valid.
 */
static PyObject *Py_is_valid_keybind(PyObject *self, PyObject *arg)
{
    Py_ssize_t size;
    const char *keybind = PyUnicode_AsUTF8AndSize(arg, &size);

    if (size == -1)
    {
        return NULL;
    }

    return PyBool_FromLong(is_valid_keybind(keybind, (size_t)size));
}

static PyMethodDef config_methods[] = {
    {"is_valid_hex_color", Py_is_valid_hex_color, METH_O, NULL},
    {"is_valid_keybind", Py_is_valid_keybind, METH_O, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef config_module = {
    PyModuleDef_HEAD_INIT,
    "_config",
    NULL,
    -1,
    config_methods};

PyMODINIT_FUNC PyInit__config(void)
{
    return PyModule_Create(&config_module);
}
