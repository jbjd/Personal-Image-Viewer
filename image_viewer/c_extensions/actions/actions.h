#ifndef PIV_ACTIONS
#define PIV_ACTIONS

#include <stdbool.h>

typedef struct
{
    PyObject_HEAD;
    PyObject *original_path;
} FileAction;

typedef struct
{
    FileAction base;
    PyObject *new_path;
} Rename;

typedef struct
{
    Rename base;
    PyObject *original_file_deleted;
} Convert;

typedef struct
{
    FileAction base;
} Delete;

#endif /* PIV_ACTIONS */
