#define INITGUID
#define PY_SSIZE_T_CLEAN

#include <fileapi.h>
#include <oleauto.h>
#include <Python.h>
#include <shlguid.h>
#include <shlwapi.h>
#include <windows.h>

#include "c_optimizations.h"
#include "b64/cencode.h"
#include "python_modules/image/read.h"

#ifdef __MINGW32__
#include <shlobj.h>
#else
#include <shlobj_core.h>
#endif

HWND g_hwnd = 0;

/**
 * Casts a PyObject representing an int to an HWND.
 *
 * @return PyLong casted HWND.
 */
static inline HWND PyLong_AsHWND(PyObject *pyLong)
{
#pragma GCC diagnostic ignored "-Wint-to-pointer-cast"
    return (HWND)PyLong_AsLong(pyLong);
#pragma GCC diagnostic pop
}

/**
 * Sets clipboard data and format.
 *
 * @param format UINT format that the windows clipboard supports
 * @param data to set to clipboard
 * @return WINBOOL that's true when successful. If it fails, call GetLastError for information.
 */
static inline WINBOOL _set_win_clipboard(const UINT format, void *data)
{
    return !OpenClipboard(g_hwnd) || !EmptyClipboard() || SetClipboardData(format, data) == NULL || !CloseClipboard() || 1;
}

/**
 * Copies string into a newly allocated buffer, replaces all
 * forward slashes with backslashes, and double null terminates it.
 *
 * Caller must free this malloc'ed string.
 *
 * @param str A string to normalize
 * @param size Length of provided string
 * @return Newly malloc'ed string
 */
static inline char *_normalize_str_for_file_op(const char *str, const Py_ssize_t size)
{
    Py_ssize_t i = 0;
    char *buffer = (char *)malloc((size + 2) * sizeof(char));

    for (; i < size; i++)
    {
        buffer[i] = str[i] == '/' ? '\\' : str[i];
    }
    buffer[i] = '\0';
    buffer[++i] = '\0';

    return buffer;
}

/**
 * Adds another null terminator to a string.
 *
 * Caller responsible for ensuring provided string has enough space for one additional char.
 *
 * @param str A string to double null terminate
 */
static inline void _ensure_double_null_terminated(char *str)
{
    size_t strLen = strlen(str);
    str[strLen + 1] = '\0';
}

static PyObject *init_c_utils(PyObject *self, PyObject *arg)
{
    g_hwnd = PyLong_AsHWND(arg);
    SetProcessDPIAware();

    return Py_None;
}

static PyObject *show_info(PyObject *self, PyObject *args)
{
    const char *title;
    const char *body;

    if (unlikely(!PyArg_ParseTuple(args, "ss", &title, &body)))
    {
        return NULL;
    }

    MessageBoxA(g_hwnd, body, title, 0);

    return Py_None;
}

static PyObject *ask_yes_no(PyObject *self, PyObject *args)
{
    const char *title;
    const char *body;

    if (unlikely(!PyArg_ParseTuple(args, "ss", &title, &body)))
    {
        return NULL;
    }

    int result = MessageBoxA(g_hwnd, body, title, MB_YESNO);

    return PyBool_FromLong(result == IDYES);
}

static PyObject *trash_file(PyObject *self, PyObject *arg)
{
    Py_ssize_t path_size;
    const char *path = PyUnicode_AsUTF8AndSize(arg, &path_size);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    char *path = _normalize_str_for_file_op(path, path_size);

    SHFILEOPSTRUCTA file_op = {g_hwnd, FO_DELETE, path, NULL, FOF_ALLOWUNDO | FOF_FILESONLY | FOF_NOCONFIRMATION | FOF_NOERRORUI};
    SHFileOperationA(&file_op);

    free(path);

    Py_END_ALLOW_THREADS;

    return Py_None;
}

static PyObject *restore_file(PyObject *self, PyObject *arg)
{
    Py_ssize_t target_path_size;
    const char *raw_target_path = PyUnicode_AsUTF8AndSize(arg, &target_path_size);
    if (unlikely(raw_target_path == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    HRESULT hr;

    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);

    LPITEMIDLIST pidl_recycle_bin;
    hr = SHGetSpecialFolderLocation(g_hwnd, CSIDL_BITBUCKET, &pidl_recycle_bin);
    if (FAILED(hr))
    {
        goto end;
    }

    IShellFolder2 *recycle_bin_folder = NULL;
    hr = SHBindToObject(NULL, pidl_recycle_bin, NULL, &IID_IShellFolder2, (void **)&recycle_bin_folder);
    if (FAILED(hr))
    {
        goto fail_bind;
    }

    IEnumIDList *recycle_bin_iterator = NULL;
    hr = recycle_bin_folder->lpVtbl->EnumObjects(recycle_bin_folder, g_hwnd, SHCONTF_NONFOLDERS, &recycle_bin_iterator);
    if (FAILED(hr))
    {
        goto fail_enum;
    }

    char *target_path = _normalize_str_for_file_op(raw_target_path, target_path_size);
    target_path[0] = tolower(target_path[0]); // Bin API can return upper or lower case drives so need to normalize on something
    char *to_restore = NULL;
    DATE to_restore_recycled_time = 0;

    LPITEMIDLIST pidl_item;
    while (recycle_bin_iterator->lpVtbl->Next(recycle_bin_iterator, 1, &pidl_item, NULL) == S_OK)
    {
        STRRET deleted_file_display_name_ret;

        hr = recycle_bin_folder->lpVtbl->GetDisplayNameOf(recycle_bin_folder, pidl_item, SHGDN_INFOLDER, &deleted_file_display_name_ret);
        if (FAILED(hr))
        {
            CoTaskMemFree(pidl_item);
            continue;
        }

        char deleted_file_display_name[MAX_PATH];
        if (StrRetToBufA(&deleted_file_display_name_ret, pidl_item, deleted_file_display_name, MAX_PATH) != S_OK)
        {
            CoTaskMemFree(pidl_item);
            continue;
        }

        VARIANT variant;
        const PROPERTYKEY PKey_DisplacedFrom = {FMTID_Displaced, PID_DISPLACED_FROM};
        hr = recycle_bin_folder->lpVtbl->GetDetailsEx(recycle_bin_folder, pidl_item, &PKey_DisplacedFrom, &variant);
        if (FAILED(hr))
        {
            CoTaskMemFree(pidl_item);
            continue;
        }

        const UINT variant_length = SysStringLen(variant.bstrVal);
        const UINT deleted_file_original_path_size = variant_length + strlen(deleted_file_display_name) + 2;
        char deleted_file_original_path[deleted_file_original_path_size];
        SHUnicodeToTChar(variant.bstrVal, deleted_file_original_path, ARRAYSIZE(deleted_file_original_path));
        deleted_file_original_path[variant_length] = '\\';
        strcpy(deleted_file_original_path + variant_length + 1, deleted_file_display_name);
        deleted_file_original_path[0] = tolower(deleted_file_original_path[0]);

        if (strcmp(target_path, deleted_file_original_path))
        {
            CoTaskMemFree(pidl_item);
            continue;
        }

        const PROPERTYKEY pkey_displaced_date = {FMTID_Displaced, PID_DISPLACED_DATE};
        hr = recycle_bin_folder->lpVtbl->GetDetailsEx(recycle_bin_folder, pidl_item, &pkey_displaced_date, &variant);
        if (FAILED(hr))
        {
            CoTaskMemFree(pidl_item);
            continue;
        }

        const DATE recycled_time = variant.date;

        // Restore only the most recently recycled file of this name for consistency
        if (NULL == to_restore || to_restore_recycled_time < recycled_time)
        {
            STRRET binDisplayName;
            hr = recycle_bin_folder->lpVtbl->GetDisplayNameOf(recycle_bin_folder, pidl_item, SHGDN_FORPARSING, &binDisplayName);
            if (FAILED(hr))
            {
                CoTaskMemFree(pidl_item);
                continue;
            }

            CoTaskMemFree(to_restore);
            to_restore = CoTaskMemAlloc(MAX_PATH + 1);

            if (StrRetToBufA(&binDisplayName, pidl_item, to_restore, MAX_PATH) != S_OK)
            {
                CoTaskMemFree(pidl_item);
                continue;
            }

            _ensure_double_null_terminated(to_restore);

            to_restore_recycled_time = recycled_time;
        }

        CoTaskMemFree(pidl_item);
    }

    if (NULL != to_restore)
    {
        SHFILEOPSTRUCTA file_op = {g_hwnd, FO_MOVE, to_restore, target_path, FOF_RENAMEONCOLLISION | FOF_ALLOWUNDO | FOF_FILESONLY | FOF_NOCONFIRMATION | FOF_NOERRORUI};
        SHFileOperationA(&file_op);

        CoTaskMemFree(to_restore);
    }

    free(target_path);
fail_enum:
    recycle_bin_folder->lpVtbl->Release(recycle_bin_folder);
fail_bind:
    ILFree(pidl_recycle_bin);
end:
    CoUninitialize();
    Py_END_ALLOW_THREADS;
    return Py_None; // TODO: Could raise OS error for python code to catch
}

static PyObject *get_files_in_folder(PyObject *self, PyObject *arg)
{
    Py_ssize_t path_size;
    const char *path = PyUnicode_AsUTF8AndSize(arg, &path_size);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    PyObject *py_files = PyList_New(0);
    if (unlikely(py_files == NULL))
    {
        return NULL;
    }

    char search_query[path_size + 3];
    strcpy(search_query, path);

    const char path_last_char = path[path_size - 1];
    const char *query_end = path_last_char != '/' && path_last_char != '\\' ? "/*\0" : "*\0";
    strcat(search_query, query_end);

    struct _WIN32_FIND_DATAA file_data;
    HANDLE file_handle = FindFirstFileA(search_query, &file_data);

    if (file_handle == INVALID_HANDLE_VALUE)
    {
        goto end;
    }

    do
    {
        if ((file_data.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) == 0)
        {
            PyObject *py_file_name = Py_BuildValue("s", file_data.cFileName);
            PyList_Append(py_files, py_file_name);
            Py_DECREF(py_file_name);
        }
    } while (FindNextFileA(file_handle, &file_data));

    FindClose(file_handle);

end:
    return py_files;
}

static PyObject *open_with(PyObject *self, PyObject *arg)
{
    wchar_t *path = PyUnicode_AsWideCharString(arg, 0);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    const OPENASINFO open_as_info = {path, NULL, OAIF_EXEC | OAIF_HIDE_REGISTRATION};
    SHOpenWithDialog(g_hwnd, &open_as_info);

    Py_END_ALLOW_THREADS;

    // Unlike PyUnicode_AsUTF8, PyUnicode_AsWideCharString needs to be freed
    PyMem_Free(path);

    return Py_None;
}

static PyObject *drop_file_to_clipboard(PyObject *self, PyObject *arg)
{
    Py_ssize_t path_size;
    const char *path = PyUnicode_AsUTF8AndSize(arg, &path_size);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    size_t sizeToAlloc = sizeof(DROPFILES) + path_size + 2;

    HGLOBAL hGlobal = GlobalAlloc(GHND, sizeToAlloc);
    if (unlikely(hGlobal == NULL))
    {
        goto end;
    }

    DROPFILES *pDropFiles = (DROPFILES *)GlobalLock(hGlobal);
    if (unlikely(pDropFiles == NULL))
    {
        goto error_free_memory;
    }

    pDropFiles->pFiles = sizeof(DROPFILES);
    pDropFiles->fWide = FALSE;

    char *pathDestination = (char *)((BYTE *)pDropFiles + sizeof(DROPFILES));
    strcpy(pathDestination, path);

    GlobalUnlock(hGlobal);

    if (!_set_win_clipboard(CF_HDROP, hGlobal))
    {
    error_free_memory:
        GlobalFree(hGlobal);
    }

end:
    Py_END_ALLOW_THREADS;
    return Py_None;
}

static PyObject *read_buffer_as_base64_and_copy_to_clipboard(PyObject *self, PyObject *arg)
{
    CRawImageView *raw_image_view = (CRawImageView *)arg;
    unsigned long remaining_bytes = raw_image_view->buffer_size;
    char *buffer_start = raw_image_view->buffer;

    Py_BEGIN_ALLOW_THREADS;

    // encoded data is ~4/3 the size of the original data so make encoded buffer 2x the size.
    HGLOBAL hGlobal = GlobalAlloc(GHND, 2 * remaining_bytes);
    if (unlikely(hGlobal == NULL))
    {
        goto end;
    }

    base64_encodestate state;
    char *encoded_buffer = (char *)GlobalLock(hGlobal);
    char *encoded_buffer_position = encoded_buffer;

    if (unlikely(encoded_buffer == NULL))
    {
        GlobalFree(hGlobal);
        goto end;
    }

    base64_init_encodestate(&state);

    const unsigned long MAX_BYTES_TO_ENCODE_AT_ONCE = 1048576;
    while (remaining_bytes > 0)
    {
        unsigned bytes_to_encode = (unsigned)(remaining_bytes < MAX_BYTES_TO_ENCODE_AT_ONCE ? remaining_bytes : MAX_BYTES_TO_ENCODE_AT_ONCE);

        encoded_buffer_position += base64_encode_block(buffer_start, bytes_to_encode, encoded_buffer_position, &state);
        remaining_bytes -= bytes_to_encode;
        buffer_start += bytes_to_encode;
    }

    base64_encode_blockend(encoded_buffer, &state);

    GlobalUnlock(hGlobal);

    _set_win_clipboard(CF_TEXT, encoded_buffer);

end:
    Py_END_ALLOW_THREADS;
    return Py_None;
}

static PyMethodDef os_methods[] = {
    {"init_c_utils", init_c_utils, METH_O, NULL},
    {"show_info", show_info, METH_VARARGS, NULL},
    {"ask_yes_no", ask_yes_no, METH_VARARGS, NULL},
    {"trash_file", trash_file, METH_O, NULL},
    {"restore_file", restore_file, METH_O, NULL},
    {"get_files_in_folder", get_files_in_folder, METH_O, NULL},
    {"open_with", open_with, METH_O, NULL},
    {"drop_file_to_clipboard", drop_file_to_clipboard, METH_O, NULL},
    {"read_buffer_as_base64_and_copy_to_clipboard", read_buffer_as_base64_and_copy_to_clipboard, METH_O, NULL},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef os_module = {
    PyModuleDef_HEAD_INIT,
    "_os_nt",
    NULL,
    -1,
    os_methods};

PyMODINIT_FUNC PyInit__os_nt(void)
{
    return PyModule_Create(&os_module);
}
