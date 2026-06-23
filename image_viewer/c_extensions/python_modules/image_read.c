#define PY_SSIZE_T_CLEAN

#include "includes/image_read.h"

#include "includes/c_optimizations.h"

#include <stddef.h>
#include <turbojpeg.h>

// CRawImageView Start
static PyMemberDef CRawImageView_members[] = {
    {"view", Py_T_OBJECT_EX, offsetof(CRawImageView, view), Py_READONLY, 0},
    {"format", Py_T_OBJECT_EX, offsetof(CRawImageView, format), Py_READONLY, 0},
    {NULL}};

static void CRawImageView_dealloc(CRawImageView *self) {
    free(self->buffer);
    Py_DECREF(self->view);
    Py_DECREF(self->format);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject CRawImageView_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_read.CRawImageView",
    .tp_basicsize = sizeof(CRawImageView),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .tp_dealloc = (destructor)CRawImageView_dealloc,
    .tp_members = CRawImageView_members,
};

static const char *PNG = "PNG";
static const char *JPEG = "JPEG";
static const char *GIF = "GIF";
static const char *WEBP = "WebP";
static const char *AVIF = "AVIF";
static const char *DDS = "DDS";

static inline void _magic_number_guess(PyObject *self, CRawImageView *view_buffer) {
    if (strncmp(view_buffer->buffer, "\x89PNG", 4) == 0) {
        view_buffer->format = PyObject_GetAttrString(self, VARIABLE_NAME(PNG));
    } else if (strncmp(view_buffer->buffer, "\xff\xd8\xff", 3) == 0) {
        view_buffer->format = PyObject_GetAttrString(self, VARIABLE_NAME(JPEG));
    } else if (strncmp(view_buffer->buffer, "RIFF", 4) == 0) {
        view_buffer->format = PyObject_GetAttrString(self, VARIABLE_NAME(WEBP));
    } else if (strncmp(view_buffer->buffer, "GIF8", 4) == 0) {
        view_buffer->format = PyObject_GetAttrString(self, VARIABLE_NAME(GIF));
    } else if (strncmp(view_buffer->buffer, "DDS ", 4) == 0) {
        view_buffer->format = PyObject_GetAttrString(self, VARIABLE_NAME(DDS));
    } else {
        view_buffer->format = PyObject_GetAttrString(self, VARIABLE_NAME(AVIF));
    }
}

static inline CRawImageView *CRawImageView_New(PyObject *self, PyObject *py_memory_view, char *buffer, unsigned long buffer_size) {
    CRawImageView *image_view = (CRawImageView *)PyObject_New(CRawImageView, &CRawImageView_Type);
    image_view->view = py_memory_view;
    image_view->buffer = buffer;
    image_view->buffer_size = buffer_size;
    _magic_number_guess(self, image_view);

    return image_view;
}
// CRawImageView End

// CDecodedJpegView Start
static PyMemberDef CDecodedJpegView_members[] = {
    {"dimensions", Py_T_OBJECT_EX, offsetof(CDecodedJpegView, dimensions), Py_READONLY, 0},
    {"view", Py_T_OBJECT_EX, offsetof(CDecodedJpegView, view), Py_READONLY, 0},
    {NULL}};

static void CDecodedJpegView_dealloc(CDecodedJpegView *self) {
    free(self->buffer);
    Py_DECREF(self->view);
    Py_XDECREF(self->dimensions);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject CDecodedJpegView_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_read.CDecodedJpegView",
    .tp_basicsize = sizeof(CDecodedJpegView),
    .tp_itemsize = 0,
    .tp_base = &CRawImageView_Type,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_DISALLOW_INSTANTIATION,
    .tp_dealloc = (destructor)CDecodedJpegView_dealloc,
    .tp_members = CDecodedJpegView_members,
};

static inline CDecodedJpegView *CDecodedJpegView_New(PyObject *py_memory_view, char *buffer, unsigned long buffer_size, int width, int height) {
    CDecodedJpegView *decoded_jpeg_view = (CDecodedJpegView *)PyObject_New(CDecodedJpegView, &CDecodedJpegView_Type);
    decoded_jpeg_view->view = py_memory_view;
    decoded_jpeg_view->buffer = buffer;
    decoded_jpeg_view->buffer_size = buffer_size;
    decoded_jpeg_view->dimensions = Py_BuildValue("(ii)", width, height);

    return decoded_jpeg_view;
}
// CDecodedJpegView End

static PyObject *read_image_into_buffer(PyObject *self, PyObject *arg) {
    const char *path = PyUnicode_AsUTF8(arg);
    if (unlikely(path == NULL)) {
        return NULL;
    }

    FILE *file = fopen(path, "rb");
    if (file == NULL) {
        return Py_None;
    }

    fseek(file, 0, SEEK_END);
    const long size = ftell(file);
    fseek(file, 0, SEEK_SET);

    if (unlikely(size < 0)) {
        fclose(file);
        goto error;
    }

    char *buffer = (char *)malloc(size * sizeof(char));
    if (unlikely(buffer == NULL)) {
        fclose(file);
        goto error;
    }

    const size_t read_bytes = fread(buffer, sizeof(char), size, file);
    fclose(file);
    if (unlikely(read_bytes != size)) {
        goto error;
    }

    PyObject *py_memory_view = PyMemoryView_FromMemory(buffer, size, PyBUF_READ);
    if (unlikely(py_memory_view == NULL)) {
        goto error;
    }

    return (PyObject *)CRawImageView_New(self, py_memory_view, buffer, size);
error:
    return Py_None;
}

/**
 * Downcales dimension by ratio of numerator over `downscale_factor`.
 *
 * @param dimension int to scale
 * @param downscale_factor of ratio to scale by
 * @return Scaled value
 */
static inline int get_downscaled_dimension(int dimension, int downscale_factor) {
    return (dimension + downscale_factor - 1) / downscale_factor;
}

static PyObject *decode_jpeg_downscaled(PyObject *self, PyObject *const *args, Py_ssize_t nargs) {
    if (unlikely(nargs != 2)) {
        PyErr_SetString(PyExc_TypeError, "");
        return NULL;
    }

    CRawImageView *raw_image_view = (CRawImageView *)args[0];

    tjhandle decompress_handle = tjInitDecompress();
    if (unlikely(decompress_handle == NULL)) {
        return NULL;
    }

    int width, height;
    if (unlikely(tjDecompressHeader(decompress_handle, (unsigned char *)raw_image_view->buffer, raw_image_view->buffer_size, &width, &height) < 0)) {
        goto error_free_handle;
    }

    const int pixel_format = TJPF_RGB;
    const int pixel_size = tjPixelSize[pixel_format];

    const long downscale_factor = PyLong_AsLong(args[1]);
    const int scaled_width = get_downscaled_dimension(width, downscale_factor);
    const int scaled_height = get_downscaled_dimension(height, downscale_factor);

    unsigned long resized_jpeg_buffer_size = scaled_width * scaled_height * pixel_size * sizeof(char);
    char *resized_jpeg_buffer = (char *)malloc(resized_jpeg_buffer_size);
    if (unlikely(resized_jpeg_buffer == NULL)) {
        goto error_free_handle;
    }

    if (unlikely(tjDecompress2(
                     decompress_handle,
                     (unsigned char *)raw_image_view->buffer,
                     raw_image_view->buffer_size,
                     (unsigned char *)resized_jpeg_buffer,
                     scaled_width,
                     0,
                     scaled_height,
                     pixel_format,
                     0) < 0)) {
        goto error_free_buffer;
    }

    PyObject *py_jpeg_memory_view = PyMemoryView_FromMemory(resized_jpeg_buffer, resized_jpeg_buffer_size, PyBUF_READ);
    if (unlikely(py_jpeg_memory_view == NULL)) {
        goto error_free_buffer;
    }

    tjDestroy(decompress_handle);
    return (PyObject *)CDecodedJpegView_New(py_jpeg_memory_view, resized_jpeg_buffer, resized_jpeg_buffer_size, scaled_width, scaled_height);

error_free_buffer:
    free(resized_jpeg_buffer);
error_free_handle:
    tjDestroy(decompress_handle);
    return NULL;
}

static PyMethodDef image_read_methods[] = {
    {"read_image_into_buffer", read_image_into_buffer, METH_O, NULL},
    {"decode_jpeg_downscaled", (PyCFunction)decode_jpeg_downscaled, METH_FASTCALL, NULL},
    {NULL, NULL, 0, NULL}};

static int image_read_exec(PyObject *module) {
    if (unlikely(
            PyType_Ready(&CRawImageView_Type) ||
            PyType_Ready(&CDecodedJpegView_Type) ||
            PyModule_AddObjectRef(module, VARIABLE_NAME(CRawImageView), (PyObject *)&CRawImageView_Type) ||
            PyModule_AddObjectRef(module, VARIABLE_NAME(CDecodedJpegView), (PyObject *)&CDecodedJpegView_Type) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(PNG), PNG) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(JPEG), JPEG) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(GIF), GIF) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(WEBP), WEBP) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(AVIF), AVIF) ||
            PyModule_AddStringConstant(module, VARIABLE_NAME(DDS), DDS))) {
        Py_DECREF(module);
        return -1;
    }

    return 0;
}

static PyModuleDef_Slot image_read_slots[] = {
    {Py_mod_exec, image_read_exec},
    {Py_mod_multiple_interpreters, Py_MOD_MULTIPLE_INTERPRETERS_NOT_SUPPORTED},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}};

static struct PyModuleDef image_read_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_read",
    .m_size = 0,
    .m_methods = image_read_methods,
    .m_slots = image_read_slots};

PyMODINIT_FUNC PyInit__read(void) {
    return PyModuleDef_Init(&image_read_module);
}