#include <Python.h>

#include "./c_optimizations.h"

// FileAction Start
typedef struct
{
    PyObject_HEAD;
    PyObject *original_path;
} FileAction;

static PyMemberDef FileAction_members[] = {
    {"original_path", Py_T_OBJECT_EX, offsetof(FileAction, original_path), 0, NULL},
    {NULL}};

static int FileAction_init(FileAction *self, PyObject *args, PyObject *kwds)
{
    PyObject *original_path = NULL;

    if (unlikely(!PyArg_ParseTuple(args, "O", &original_path)))
    {
        return -1;
    }

    Py_XDECREF(self->original_path);
    Py_INCREF(original_path);
    self->original_path = original_path;

    return 0;
}

static PyTypeObject FileAction_Type;
static PyObject *FileAction_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
#ifdef DEV_CHECKS
    if (type == &FileAction_Type)
    {
        PyErr_SetString(PyExc_TypeError, "Cannot instantiate abstract class FileAction");
        return NULL;
    }
#endif

    FileAction *self;

    self = (FileAction *)type->tp_alloc(type, 0);
    if (unlikely(self == NULL))
    {
        return NULL;
    }

    self->original_path = NULL;

    return (PyObject *)self;
}

static void FileAction_dealloc(FileAction *self)
{
    Py_XDECREF(self->original_path);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject FileAction_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_abstract_classes.FileAction",
    .tp_basicsize = sizeof(FileAction),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = FileAction_new,
    .tp_init = (initproc)FileAction_init,
    .tp_dealloc = (destructor)FileAction_dealloc,
    .tp_members = FileAction_members,
};
// FileAction End

// UIElementBase Start
typedef struct
{
    PyObject_HEAD;
    PyObject *id;
} UIElementBase;

static PyMemberDef UIElementBase_members[] = {
    {"id", Py_T_OBJECT_EX, offsetof(UIElementBase, id), 0, NULL},
    {NULL}};

static int UIElementBase_init(UIElementBase *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"id", NULL};
    PyObject *id = NULL;

    if (unlikely(!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &id)))
    {
        return -1;
    }

    if (id == NULL)
    {
        id = PyLong_FromLong(-1);
    }

    Py_XDECREF(self->id);
    Py_INCREF(id);
    self->id = id;

    return 0;
}

static PyTypeObject UIElementBase_Type;
static PyObject *UIElementBase_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
#ifdef DEV_CHECKS
    if (type == &UIElementBase_Type)
    {
        PyErr_SetString(PyExc_TypeError, "Cannot instantiate abstract class UIElementBase");
        return NULL;
    }
#endif

    UIElementBase *self;

    self = (UIElementBase *)type->tp_alloc(type, 0);
    if (unlikely(self == NULL))
    {
        return NULL;
    }

    self->id = NULL;

    return (PyObject *)self;
}

static void UIElementBase_dealloc(UIElementBase *self)
{
    Py_XDECREF(self->id);
    Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyTypeObject UIElementBase_Type = {
    .ob_base = PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_abstract_classes.UIElementBase",
    .tp_basicsize = sizeof(UIElementBase),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = UIElementBase_new,
    .tp_init = (initproc)UIElementBase_init,
    .tp_dealloc = (destructor)UIElementBase_dealloc,
    .tp_members = UIElementBase_members,
};
// UIElementBase End

static struct PyModuleDef abstract_classes_module = {
    PyModuleDef_HEAD_INIT,
    "_abstract_classes",
    NULL,
    -1};

PyMODINIT_FUNC PyInit__abstract_classes(void)
{
    if (unlikely(
            PyType_Ready(&FileAction_Type) < 0 ||
            PyType_Ready(&UIElementBase_Type) < 0))
    {
        return NULL;
    }

    PyObject *module = PyModule_Create(&abstract_classes_module);

    if (unlikely(
            PyModule_AddObjectRef(module, "FileAction", (PyObject *)&FileAction_Type) < 0 ||
            PyModule_AddObjectRef(module, "UIElementBase", (PyObject *)&UIElementBase_Type) < 0))
    {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
