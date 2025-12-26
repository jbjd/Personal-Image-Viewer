#include <Python.h>

#include "../c_optimizations.h"

typedef struct
{
    PyObject_HEAD;
    PyObject *id;
} UIElementBase;

static PyMemberDef UIElementBase_members[] = {
    {"id", Py_T_OBJECT_EX, offsetof(UIElementBase, id), Py_READONLY, NULL},
    {NULL}};

static int UIElementBase_init(UIElementBase *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"id", NULL};
    PyObject *id = NULL;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|O", kwlist, &id))
    {
        return -1;
    }

    if (id == NULL)
    {
        return -1;
    }

    Py_XDECREF(self->id);
    Py_INCREF(id);
    self->id = id;

    return 0;
}

static PyObject *UIElementBase_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    UIElementBase *self;

    self = (UIElementBase *)type->tp_alloc(type, 0);
    if (self == NULL)
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

static struct PyModuleDef abstract_classes_module = {
    PyModuleDef_HEAD_INIT,
    "_abstract_classes",
    NULL,
    -1};

PyMODINIT_FUNC PyInit__abstract_classes(void)
{
    if (unlikely(PyType_Ready(&UIElementBase_Type) < 0))
    {
        return NULL;
    }

    PyObject *module = PyModule_Create(&abstract_classes_module);

    if (unlikely(PyModule_AddObjectRef(module, "UIElementBase", (PyObject *)&UIElementBase_Type) < 0))
    {
        Py_DECREF(module);
        return NULL;
    }

    return module;
}
