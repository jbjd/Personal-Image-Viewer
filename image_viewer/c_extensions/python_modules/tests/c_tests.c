#include <Python.h>

#include "c_optimizations.h"
#include "../config/_utils.h"

/**
 * Wraps is_valid_hex_color so it can be called in Python.
 *
 * @param self Instance of this module
 * @param arg A PyUnicode string to check
 * @return PyBool if valid
 */
static PyObject *Py_is_valid_hex_color(PyObject *self, PyObject *arg)
{
    Py_ssize_t size;
    const char *hex = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1))
    {
        return NULL;
    }

    return PyBool_FromLong(is_valid_hex_color(hex));
}

/**
 * Wraps is_valid_keybind so it can be called in Python.
 *
 * @param self Instance of this module
 * @param arg A PyUnicode string to check
 * @return PyBool if valid
 */
static PyObject *Py_is_valid_keybind(PyObject *self, PyObject *arg)
{
    Py_ssize_t size;
    const char *keybind = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1))
    {
        return NULL;
    }

    return PyBool_FromLong(is_valid_keybind(keybind, (size_t)size));
}

static PyMethodDef test_utils_methods[] = {
    {"is_valid_hex_color", Py_is_valid_hex_color, METH_O, NULL},
    {"is_valid_keybind", Py_is_valid_keybind, METH_O, NULL},
    {NULL, NULL, 0, NULL}};

static int test_utils_exec(PyObject *Py_UNUSED(module))
{
    return 0;
}

static PyModuleDef_Slot test_utils_slots[] = {
    {Py_mod_exec, test_utils_exec},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}};

static struct PyModuleDef test_utils_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_c_tests",
    .m_size = 0,
    .m_methods = test_utils_methods,
    .m_slots = test_utils_slots};

PyMODINIT_FUNC PyInit__c_tests(void)
{
    return PyModuleDef_Init(&test_utils_module);
}