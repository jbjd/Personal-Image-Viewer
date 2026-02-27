#ifndef PIV_ACTIONS
#define PIV_ACTIONS

typedef struct
{
    PyObject_HEAD;
    PyObject *original_path;
} FileAction;

typedef struct
{
    FileAction base;
} Delete;

#endif /* PIV_ACTIONS */
