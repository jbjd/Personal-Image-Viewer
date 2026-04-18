#define PY_SSIZE_T_CLEAN

#include <Python.h>

#include "c_optimizations.h"
#include "b64/cencode.h"
#include "python_modules/image/read.h"
#include "_utils.h"

static PyObject *read_buffer_as_base64(PyObject *self, PyObject *arg)
{
    CMemoryViewBuffer *memoryViewBuffer = (CMemoryViewBuffer *)arg;
    unsigned long buffer_size = memoryViewBuffer->bufferSize;
    char *buffer = memoryViewBuffer->buffer;

    char *encoded_buffer;

    Py_BEGIN_ALLOW_THREADS;

    // encoded data is ~4/3 the size of the original data so make encoded buffer 2x the size.
    encoded_buffer = (char *)malloc(2 * buffer_size * sizeof(char));
    if (unlikely(encoded_buffer == NULL))
    {
        return NULL;
    }

    encode_buffer_base64(buffer, buffer_size, encoded_buffer);

    Py_END_ALLOW_THREADS;
    return PyUnicode_FromString(encoded_buffer);
}

static PyMethodDef os_methods[] = {
    {"read_buffer_as_base64", read_buffer_as_base64, METH_O, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef os_module = {
    PyModuleDef_HEAD_INIT,
    "_os_linux",
    NULL,
    -1,
    os_methods};

PyMODINIT_FUNC PyInit__os_linux(void)
{
    return PyModule_Create(&os_module);
}
