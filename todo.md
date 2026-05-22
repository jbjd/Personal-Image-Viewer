# A

To migrate your Python C extension from single-phase to multi-phase initialization (PEP 489), you must split your logic into a creation phase (which defines the module) and an execution phase (which populates it). This modernizes your module, enabling proper sub-interpreter support and per-module state.Step-by-Step Migration GuideExtract your initialization logic:Move all code that creates classes, defines constants, and adds methods out of the old PyInit_<module> function and into a new "exec" callback function (e.g., my_module_exec).Remove module creation calls:Remove calls like PyModule_Create from your primary init function.Define execution slots:Add a m_slots array to your PyModuleDef struct that points to your new exec function.Update the entry point:Update PyInit_<module> to return PyModuleDef_Init.

---Before---

```python
static struct PyModuleDef my_module_def = {
    PyModuleDef_HEAD_INIT,
    "my_module",
    "Module docstring",
    -1, // Global state
    my_methods
};

PyMODINIT_FUNC PyInit_my_module(void) {
    PyObject *m = PyModule_Create(&my_module_def);
    if (m == NULL) return NULL;
    
    PyModule_AddObject(m, "SomeConstant", PyLong_FromLong(42));
    return m;
}
```

---After---

```python
#include <Python.h>

// 1. Execution function
static int my_module_exec(PyObject *m) {
    // Populate the module here
    if (PyModule_AddObject(m, "SomeConstant", PyLong_FromLong(42)) < 0) {
        return -1;
    }
    return 0;
}

// 2. Define slots
static PyModuleDef_Slot my_module_slots[] = {
    {Py_mod_exec, my_module_exec},
    #ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED}, // Indicate GIL-neutrality if needed
    #endif
    {0, NULL}
};

// 3. Define module with slots and 0 size (or >0 for module state)
static struct PyModuleDef my_module_def = {
    PyModuleDef_HEAD_INIT,
    "my_module",
    "Module docstring",
    0, // m_size: Set to 0 if no module-level state, or >0 if storing state on the module
    my_methods,
    my_module_slots
};

// 4. Update primary init
PyMODINIT_FUNC PyInit_my_module(void) {
    return PyModuleDef_Init(&my_module_def);
}
```