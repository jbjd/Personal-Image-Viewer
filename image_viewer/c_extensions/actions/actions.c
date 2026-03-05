#include <Python.h>

#include "../c_optimizations.h"
#include "actions.h"

// FileAction Start
static PyMemberDef FileAction_members[] = {
    {"original_path", Py_T_OBJECT_EX, offsetof(FileAction, original_path), Py_READONLY, 0},
    {NULL}};

static void FileAction_init_set(FileAction *self, PyObject *original_path)
{
    Py_XDECREF(self->original_path);
    Py_INCREF(original_path);
    self->original_path = original_path;
}

static int FileAction_init(FileAction *self, PyObject *args, PyObject *kwds)
{
    PyObject *original_path;

    if (!PyArg_ParseTuple(args, "O", &original_path))
    {
        PyErr_SetString(PyExc_TypeError, "FileAction.__init__ takes 1 positional argument");
        return -1;
    }

    FileAction_init_set(self, original_path);

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
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE | Py_TPFLAGS_IS_ABSTRACT | Py_TPFLAGS_BASETYPE,
    .tp_init = (initproc)FileAction_init,
    .tp_dealloc = (destructor)FileAction_dealloc,
    .tp_members = FileAction_members,
};
// FileAction End

// Rename Start
static PyObject *Rename_get_undo_message(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    Rename *self_rename = (Rename *)self;

    return PyUnicode_FromFormat("Rename %U back to %U?", self_rename->new_path, self_rename->base.original_path);
}

static PyMethodDef Rename_methods[] = {
    {"get_undo_message", Rename_get_undo_message, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}};

static PyMemberDef Rename_members[] = {
    {"new_path", Py_T_OBJECT_EX, offsetof(Rename, new_path), Py_READONLY, 0},
    {NULL}};

static void Rename_init_set(Rename *self, PyObject *original_path, PyObject *new_path)
{
    FileAction_init_set(&self->base, original_path);

    Py_XDECREF(self->new_path);
    Py_INCREF(new_path);
    self->new_path = new_path;
}

static int Rename_init(Rename *self, PyObject *args, PyObject *kwds)
{
    PyObject *original_path;
    PyObject *new_path;

    if (!PyArg_ParseTuple(args, "OO", &original_path, &new_path))
    {
        PyErr_SetString(PyExc_TypeError, "Rename.__init__ takes 2 positional arguments");
        return -1;
    }

    Rename_init_set(self, original_path, new_path);

    return 0;
}

static void Rename_dealloc(Rename *self)
{
    Py_XDECREF(self->new_path);
    FileAction_dealloc(&self->base);
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
    .tp_methods = Rename_methods,
    .tp_members = Rename_members,
};
// Rename End

// Convert Start
static PyObject *Convert_get_undo_message(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    Convert *self_convert = (Convert *)self;

    return self_convert->original_file_deleted == Py_True
               ? PyUnicode_FromFormat("Delete %U and restore %U from trash?", self_convert->base.new_path, self_convert->base.base.original_path)
               : PyUnicode_FromFormat("Delete %U?", self_convert->base.new_path);
}

static PyMethodDef Convert_methods[] = {
    {"get_undo_message", Convert_get_undo_message, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}};

static PyMemberDef Convert_members[] = {
    {"original_file_deleted", Py_T_OBJECT_EX, offsetof(Convert, original_file_deleted), Py_READONLY, 0},
    {NULL}};

static int Convert_init(Convert *self, PyObject *args, PyObject *kwds)
{
    PyObject *original_path;
    PyObject *new_path;
    PyObject *original_file_deleted;

    if (!PyArg_ParseTuple(args, "OOO", &original_path, &new_path, &original_file_deleted))
    {
        PyErr_SetString(PyExc_TypeError, "Convert.__init__ takes 3 positional arguments");
        return -1;
    }

    Rename_init_set(&self->base, original_path, new_path);

    Py_XDECREF(self->original_file_deleted);
    Py_INCREF(original_file_deleted);
    self->original_file_deleted = original_file_deleted;

    return 0;
}

static void Convert_dealloc(Convert *self)
{
    Rename_dealloc(&self->base);
}

static PyTypeObject Convert_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_actions.Convert",
    .tp_basicsize = sizeof(Convert),
    .tp_itemsize = 0,
    .tp_base = &Rename_Type,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Convert_init,
    .tp_dealloc = (destructor)Convert_dealloc,
    .tp_methods = Convert_methods,
    .tp_members = Convert_members,
};
// Convert End

// Delete Start
static PyObject *Delete_get_undo_message(PyObject *self, PyObject *Py_UNUSED(ignored))
{
    Delete *self_delete = (Delete *)self;

    return PyUnicode_FromFormat("Restore %U from trash?", self_delete->base.original_path);
}

static PyMethodDef Delete_methods[] = {
    {"get_undo_message", Delete_get_undo_message, METH_NOARGS, NULL},
    {NULL, NULL, 0, NULL}};

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
    .tp_methods = Delete_methods,
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
                 PyType_Ready(&Convert_Type) < 0 ||
                 PyType_Ready(&Delete_Type) < 0))
    {
        return NULL;
    }

    PyObject *module = PyModule_Create(&actions_module);

    if (unlikely(PyModule_AddObjectRef(module, "FileAction", (PyObject *)&FileAction_Type) < 0 ||
                 PyModule_AddObjectRef(module, "Rename", (PyObject *)&Rename_Type) < 0 ||
                 PyModule_AddObjectRef(module, "Convert", (PyObject *)&Convert_Type) < 0 ||
                 PyModule_AddObjectRef(module, "Delete", (PyObject *)&Delete_Type) < 0))
    {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
