#include "includes/c_optimizations.h"
#include "includes/config.h"

#include <Python.h>

/**
 * Wraps is_valid_hex_color so it can be called in Python.
 *
 * @param self Instance of this module
 * @param arg A PyUnicode string to check
 * @return PyBool if valid
 */
static PyObject *Py_is_valid_hex_color(PyObject *self, PyObject *arg) {
    Py_ssize_t size;
    const char *hex = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1)) {
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
static PyObject *Py_is_valid_keybind(PyObject *self, PyObject *arg) {
    Py_ssize_t size;
    const char *keybind = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1)) {
        return NULL;
    }

    return PyBool_FromLong(is_valid_keybind(keybind, (size_t)size));
}

static inline bool _has_quotes(const char *str, Py_ssize_t size) {
    return size > 1 && (str[0] == '"' || str[size - 1] == '\'') && str[0] == str[size - 1];
}

/**
 * Checks if a string is empty or contains a valid hex color
 *
 * @param self Instance of this module
 * @param arg A PyUnicode string to check
 * @return PyBool if valid or empty
 */
static PyObject *Py_is_empty_or_valid_hex_color(PyObject *self, PyObject *arg) {
    Py_ssize_t size;
    const char *hex = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1)) {
        return NULL;
    }

    const bool has_quotes = _has_quotes(hex, size);
    if (has_quotes) {
        size -= 2;
    }

    if (size == 0) {
        return Py_True;
    }
    if (size != 7) {
        return Py_False;
    }

    char *parsed_hex = malloc(8 * sizeof(char));
    strncpy(parsed_hex, hex + has_quotes, 7);
    parsed_hex[7] = '\0';

    bool is_valid = is_valid_hex_color(parsed_hex);
    free(parsed_hex);

    return PyBool_FromLong(is_valid);
}

/**
 * Checks if a string is empty or contains a valid keybind
 *
 * @param self Instance of this module
 * @param arg A PyUnicode string to check
 * @return PyBool if valid or empty
 */
static PyObject *Py_is_empty_or_valid_keybind(PyObject *self, PyObject *arg) {
    Py_ssize_t size;
    const char *keybind = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1)) {
        return NULL;
    }

    const bool has_quotes = _has_quotes(keybind, size);
    if (has_quotes) {
        size -= 2;
    }

    if (size == 0) {
        return Py_True;
    }

    char *parsed_keybind = malloc((size + 1) * sizeof(char));
    memcpy(parsed_keybind, keybind + has_quotes, size);
    parsed_keybind[size] = '\0';

    bool is_valid = is_valid_keybind(parsed_keybind, size);
    free(parsed_keybind);

    return PyBool_FromLong(is_valid);
}

/**
 * Checks if a string is empty or contains a valid integer
 *
 * @param self Instance of this module
 * @param arg A PyUnicode string to check
 * @return PyBool if valid or empty
 */
static PyObject *Py_is_empty_or_valid_int(PyObject *self, PyObject *arg) {
    Py_ssize_t size;
    const char *integer = PyUnicode_AsUTF8AndSize(arg, &size);

    if (unlikely(size == -1)) {
        return NULL;
    }

    int index = _has_quotes(integer, size);
    size_t end = size;
    if (index) {
        --end;
    }

    if (index == end) {
        return Py_True;
    }

    if (integer[index] == '-') {
        ++index;
    }

    while (index < end) {
        if (!isdigit(integer[index])) {
            return Py_False;
        }
        ++index;
    }

    return Py_True;
}

static PyMethodDef c_bindings_methods[] = {
    {"is_valid_hex_color", Py_is_valid_hex_color, METH_O, NULL},
    {"is_valid_keybind", Py_is_valid_keybind, METH_O, NULL},
    {"is_empty_or_valid_hex_color", Py_is_empty_or_valid_hex_color, METH_O, NULL},
    {"is_empty_or_valid_keybind", Py_is_empty_or_valid_keybind, METH_O, NULL},
    {"is_empty_or_valid_int", Py_is_empty_or_valid_int, METH_O, NULL},
    {NULL, NULL, 0, NULL}};

static int c_bindings_exec(PyObject *Py_UNUSED(module)) {
    return 0;
}

static PyModuleDef_Slot c_bindings_slots[] = {
    {Py_mod_exec, c_bindings_exec},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}};

static struct PyModuleDef c_bindings_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_c_bindings",
    .m_size = 0,
    .m_methods = c_bindings_methods,
    .m_slots = c_bindings_slots};

PyMODINIT_FUNC PyInit__c_bindings(void) {
    return PyModuleDef_Init(&c_bindings_module);
}