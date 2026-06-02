#ifndef PIV_IMAGE_READ
#define PIV_IMAGE_READ

#include <Python.h>

typedef struct
{
    PyObject_HEAD;
    char *buffer;
    unsigned long buffer_size;
    PyObject *view;
    PyObject *format;
} CRawImageView;

typedef struct
{
    PyObject_HEAD;
    char *buffer;
    unsigned long buffer_size;
    PyObject *view;
    PyObject *dimensions;
} CDecodedJpegView;

#endif /* PIV_IMAGE_READ */
