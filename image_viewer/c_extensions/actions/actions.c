#include <Python.h>

#include "../c_optimizations.h"
#include "actions.h"

// FileAction Start
static PyMemberDef FileAction_members[] = {
    {"original_path", Py_T_OBJECT_EX, offsetof(FileAction, original_path), Py_READONLY, 0},
    {NULL}};

static int FileAction_init(FileAction *self, PyObject *args, PyObject *kwds)
{
    PyObject *original_path;

    if (!PyArg_ParseTuple(args, "O", &original_path))
    {
        PyErr_SetString(PyExc_TypeError, "FileAction.__init__ takes 1 positional argument");
        return -1;
    }

    Py_XDECREF(self->original_path);
    Py_INCREF(original_path);
    self->original_path = original_path;

    return 0;
}

static void FileAction_dealloc(FileAction *self)
{
    Py_XDECREF(self->original_path);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject FileAction_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_actions.FileAction",
    .tp_basicsize = sizeof(FileAction),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_DISALLOW_INSTANTIATION | Py_TPFLAGS_BASETYPE,
    .tp_init = (initproc)FileAction_init,
    .tp_dealloc = (destructor)FileAction_dealloc,
    .tp_members = FileAction_members,
};
// FileAction End

// Rename Start
static PyMemberDef Rename_members[] = {
    {"new_path", Py_T_OBJECT_EX, offsetof(Rename, new_path), Py_READONLY, 0},
    {NULL}};

static int Rename_init(Rename *self, PyObject *args, PyObject *kwds)
{
    PyObject *original_path;
    PyObject *new_path;

    if (!PyArg_ParseTuple(args, "OO", &original_path, &new_path))
    {
        PyErr_SetString(PyExc_TypeError, "Rename.__init__ takes 2 positional arguments");
        return -1;
    }

    Py_XDECREF(self->base.original_path);
    Py_INCREF(original_path);
    self->base.original_path = original_path;

    Py_XDECREF(self->new_path);
    Py_INCREF(new_path);
    self->new_path = new_path;

    return 0;
}

static void Rename_dealloc(Rename *self)
{
    Py_XDECREF(self->new_path);
    FileAction_dealloc((FileAction *)self);
}

static PyTypeObject Rename_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_actions.Rename",
    .tp_basicsize = sizeof(Rename),
    .tp_itemsize = 0,
    .tp_base = &FileAction_Type,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Rename_init,
    .tp_dealloc = (destructor)Rename_dealloc,
    .tp_members = Rename_members,
};
// Rename End

// Delete Start
static int Delete_init(Delete *self, PyObject *args, PyObject *kwds)
{
    return FileAction_init((FileAction *)self, args, kwds);
}

static void Delete_dealloc(Delete *self)
{
    FileAction_dealloc((FileAction *)self);
}

static PyTypeObject Delete_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_actions.Delete",
    .tp_basicsize = sizeof(Delete),
    .tp_itemsize = 0,
    .tp_base = &FileAction_Type,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Delete_init,
    .tp_dealloc = (destructor)Delete_dealloc,
};
// Delete End

static struct PyModuleDef actions_module = {
    PyModuleDef_HEAD_INIT,
    "_actions",
    NULL,
    -1,
    NULL};

PyMODINIT_FUNC PyInit__actions(void)
{
    if (unlikely(PyType_Ready(&FileAction_Type) < 0 ||
                 PyType_Ready(&Rename_Type) < 0 ||
                 PyType_Ready(&Delete_Type) < 0))
    {
        return NULL;
    }

    PyObject *module = PyModule_Create(&actions_module);

    if (unlikely(PyModule_AddObjectRef(module, "FileAction", (PyObject *)&FileAction_Type) < 0 ||
                 PyModule_AddObjectRef(module, "Rename", (PyObject *)&Rename_Type) < 0 ||
                 PyModule_AddObjectRef(module, "Delete", (PyObject *)&Delete_Type) < 0))
    {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
