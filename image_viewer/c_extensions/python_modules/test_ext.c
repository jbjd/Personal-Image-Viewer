#include "includes/c_optimizations.h"
#include "includes/config.h"

#include <Python.h>

#ifdef _WIN32
#include <windows.h>
#endif

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

    return PyBool_FromLong(is_valid_keybind(keybind));
}

#ifdef _WIN32
/**
 * Returns clipboard contents as PyUnicode string
 *
 * @param self Instance of this module
 * @return PyUnicode string of clipboard contents
 */
static PyObject *Py_read_clipboard(PyObject *self) {
    if (!OpenClipboard(0)) {
        PyErr_SetString(PyExc_OSError, "Failed to open clipboard");
    }

    HANDLE h_clipboard = GetClipboardData(CF_UNICODETEXT);

    if (h_clipboard == NULL) {
        PyErr_SetString(PyExc_OSError, "Failed to read clipboard");
    }

    wchar_t *clipboard_content = (wchar_t *)GlobalLock(h_clipboard);
    PyObject *as_string = PyUnicode_FromWideChar(clipboard_content, -1);
    GlobalUnlock(h_clipboard);

    CloseClipboard();
    return as_string;
}
#endif

static PyMethodDef c_bindings_methods[] = {
    {"is_valid_hex_color", Py_is_valid_hex_color, METH_O, NULL},
    {"is_valid_keybind", Py_is_valid_keybind, METH_O, NULL},
#ifdef _WIN32
    {"read_clipboard", (PyCFunction)Py_read_clipboard, METH_NOARGS, NULL},
#endif
    {NULL, NULL, 0, NULL}
};

static int c_bindings_exec(PyObject *Py_UNUSED(module)) {
    return 0;
}

static PyModuleDef_Slot c_bindings_slots[] = {
    {Py_mod_exec, c_bindings_exec},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static struct PyModuleDef c_bindings_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_c_bindings",
    .m_size = 0,
    .m_methods = c_bindings_methods,
    .m_slots = c_bindings_slots
};

PyMODINIT_FUNC PyInit__c_bindings(void) {
    return PyModuleDef_Init(&c_bindings_module);
}
