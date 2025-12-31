#define INITGUID
#define PY_SSIZE_T_CLEAN

#include <fileapi.h>
#include <oleauto.h>
#include <Python.h>
#include <shlguid.h>
#include <shlwapi.h>
#include <windows.h>

#include "../c_optimizations.h"
#include "b64/cencode.h"
#include "image/read.h"

#ifdef __MINGW32__
#include <shlobj.h>
#else
#include <shlobj_core.h>
#endif

HWND g_hwnd = 0;

/**
 * Given a PyObject representing an int in Python,
 * cast it to an HWND.
 *
 * Returns casted HWND.
 */
static inline HWND PyLong_AsHWND(PyObject *pyLong)
{
#pragma GCC diagnostic ignored "-Wint-to-pointer-cast"
    return (HWND)PyLong_AsLong(pyLong);
#pragma GCC diagnostic pop
}

/**
 * Given some data, opens, emptys, sets, and closes clipboard
 * with provided data.
 *
 * Returns WINBOOL of if successful. If it fails, call GetLastError for information.
 */
static inline WINBOOL set_win_clipboard(const UINT format, void *data)
{
    return !OpenClipboard(g_hwnd) || !EmptyClipboard() || SetClipboardData(format, data) == NULL || !CloseClipboard() || 1;
}

/**
 * Copies string into a newly allocated buffer, replaces all
 * forward slashes with backslashes, and double null terminates it.
 *
 * Caller must free this string.
 */
static inline char *normalize_str_for_file_op(const char *str, const Py_ssize_t size)
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
 */
static inline void ensure_double_null_terminated(char *str)
{
    size_t strLen = strlen(str);
    str[strLen + 1] = '\0';
}


/**
 * Sets the hwnd value for all functions called in this module.
 * hwnd will be 0 until this is set.
 */
static PyObject *set_hwnd(PyObject *self, PyObject *arg)
{
    g_hwnd = PyLong_AsHWND(arg);

    return Py_None;
}


static PyObject *trash_file(PyObject *self, PyObject *arg)
{
    Py_ssize_t rawPathSize;
    const char *rawPath = PyUnicode_AsUTF8AndSize(arg, &rawPathSize);
    if (unlikely(rawPath == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    char *path = normalize_str_for_file_op(rawPath, rawPathSize);

    SHFILEOPSTRUCTA fileOp = {g_hwnd, FO_DELETE, path, NULL, FOF_ALLOWUNDO | FOF_FILESONLY | FOF_NOCONFIRMATION | FOF_NOERRORUI};
    SHFileOperationA(&fileOp);

    free(path);

    Py_END_ALLOW_THREADS;

    return Py_None;
}

static PyObject *restore_file(PyObject *self, PyObject *arg)
{
    Py_ssize_t rawOriginalPathSize;
    const char *rawOriginalPath = PyUnicode_AsUTF8AndSize(arg, &rawOriginalPathSize);
    if (unlikely(rawOriginalPath == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    HRESULT hr;

    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);

    LPITEMIDLIST pidlRecycleBin;
    hr = SHGetSpecialFolderLocation(g_hwnd, CSIDL_BITBUCKET, &pidlRecycleBin);
    if (FAILED(hr))
    {
        goto end;
    }

    IShellFolder2 *recycleBinFolder = NULL;
    hr = SHBindToObject(NULL, pidlRecycleBin, NULL, &IID_IShellFolder2, (void **)&recycleBinFolder);
    if (FAILED(hr))
    {
        goto fail_bind;
    }

    IEnumIDList *recycleBinIterator = NULL;
    hr = recycleBinFolder->lpVtbl->EnumObjects(recycleBinFolder, g_hwnd, SHCONTF_NONFOLDERS, &recycleBinIterator);
    if (FAILED(hr))
    {
        goto fail_enum;
    }

    char *originalPath = normalize_str_for_file_op(rawOriginalPath, rawOriginalPathSize);
    originalPath[0] = tolower(originalPath[0]);  // Bin API can return upper or lower case drives so need to normalize on something
    char *targetToRestore = NULL;
    DATE targetRecycledTime = 0;

    LPITEMIDLIST pidlItem;
    while (recycleBinIterator->lpVtbl->Next(recycleBinIterator, 1, &pidlItem, NULL) == S_OK)
    {
        STRRET displayName;

        hr = recycleBinFolder->lpVtbl->GetDisplayNameOf(recycleBinFolder, pidlItem, SHGDN_INFOLDER, &displayName);
        if (FAILED(hr))
        {
            CoTaskMemFree(pidlItem);
            continue;
        }

        char displayNameBuffer[MAX_PATH];
        if (StrRetToBufA(&displayName, pidlItem, displayNameBuffer, MAX_PATH) != S_OK)
        {
            CoTaskMemFree(pidlItem);
            continue;
        }

        VARIANT variant;
        const PROPERTYKEY PKey_DisplacedFrom = {FMTID_Displaced, PID_DISPLACED_FROM};
        hr = recycleBinFolder->lpVtbl->GetDetailsEx(recycleBinFolder, pidlItem, &PKey_DisplacedFrom, &variant);
        if (FAILED(hr))
        {
            CoTaskMemFree(pidlItem);
            continue;
        }

        const UINT variantLength = SysStringLen(variant.bstrVal);
        const UINT bufferLength = variantLength + strlen(displayNameBuffer) + 2;
        char deletedFileOriginalPath[bufferLength];
        SHUnicodeToTChar(variant.bstrVal, deletedFileOriginalPath, ARRAYSIZE(deletedFileOriginalPath));
        deletedFileOriginalPath[variantLength] = '\\';
        strcpy(deletedFileOriginalPath + variantLength + 1, displayNameBuffer);
        deletedFileOriginalPath[0] = tolower(deletedFileOriginalPath[0]);

        if (strcmp(originalPath, deletedFileOriginalPath))
        {
            CoTaskMemFree(pidlItem);
            continue;
        }

        const PROPERTYKEY PKey_DisplacedDate = {FMTID_Displaced, PID_DISPLACED_DATE};
        hr = recycleBinFolder->lpVtbl->GetDetailsEx(recycleBinFolder, pidlItem, &PKey_DisplacedDate, &variant);
        if (FAILED(hr))
        {
            CoTaskMemFree(pidlItem);
            continue;
        }

        const DATE recycledTime = variant.date;

        // Restore only the most recently recycled file of this name for consistency
        if (NULL == targetToRestore || targetRecycledTime < recycledTime)
        {
            STRRET binDisplayName;
            hr = recycleBinFolder->lpVtbl->GetDisplayNameOf(recycleBinFolder, pidlItem, SHGDN_FORPARSING, &binDisplayName);
            if (FAILED(hr))
            {
                CoTaskMemFree(pidlItem);
                continue;
            }

            CoTaskMemFree(targetToRestore);
            targetToRestore = CoTaskMemAlloc(MAX_PATH + 1);

            if (StrRetToBufA(&binDisplayName, pidlItem, targetToRestore, MAX_PATH) != S_OK)
            {
                CoTaskMemFree(pidlItem);
                continue;
            }

            ensure_double_null_terminated(targetToRestore);

            targetRecycledTime = recycledTime;
        }

        CoTaskMemFree(pidlItem);
    }

    if (NULL != targetToRestore)
    {
        SHFILEOPSTRUCTA fileOp = {g_hwnd, FO_MOVE, targetToRestore, originalPath, FOF_RENAMEONCOLLISION | FOF_ALLOWUNDO | FOF_FILESONLY | FOF_NOCONFIRMATION | FOF_NOERRORUI};
        SHFileOperationA(&fileOp);

        CoTaskMemFree(targetToRestore);
    }

    free(originalPath);
fail_enum:
    recycleBinFolder->lpVtbl->Release(recycleBinFolder);
fail_bind:
    ILFree(pidlRecycleBin);
end:
    CoUninitialize();
    Py_END_ALLOW_THREADS;
    return Py_None; // TODO: Could raise OS error for python code to catch
}

static PyObject *get_files_in_folder(PyObject *self, PyObject *arg)
{
    Py_ssize_t pathSize;
    const char *path = PyUnicode_AsUTF8AndSize(arg, &pathSize);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    PyObject *pyFiles = PyList_New(0);
    if (unlikely(pyFiles == NULL))
    {
        return NULL;
    }

    char pathWithStar[pathSize + 3];
    strcpy(pathWithStar, path);

    const char pathLastChar = path[pathSize - 1];
    const char *fuzzySearchEnding = pathLastChar != '/' && pathLastChar != '\\' ? "/*\0" : "*\0";
    strcat(pathWithStar, fuzzySearchEnding);

    struct _WIN32_FIND_DATAA dirData;
    HANDLE fileHandle = FindFirstFileA(pathWithStar, &dirData);

    if (fileHandle == INVALID_HANDLE_VALUE)
    {
        goto end;
    }

    do
    {
        if ((dirData.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) == 0)
        {
            PyObject *pyFileName = Py_BuildValue("s", dirData.cFileName);
            PyList_Append(pyFiles, pyFileName);
            Py_DECREF(pyFileName);
        }
    } while (FindNextFileA(fileHandle, &dirData));

    FindClose(fileHandle);

end:
    return pyFiles;
}

static PyObject *open_with(PyObject *self, PyObject *arg)
{
    wchar_t *path = PyUnicode_AsWideCharString(arg, 0);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    const OPENASINFO openAsInfo = {path, NULL, OAIF_EXEC | OAIF_HIDE_REGISTRATION};
    SHOpenWithDialog(g_hwnd, &openAsInfo);

    Py_END_ALLOW_THREADS;

    // Unlike PyUnicode_AsUTF8, PyUnicode_AsWideCharString needs to be freed
    PyMem_Free(path);

    return Py_None;
}

static PyObject *drop_file_to_clipboard(PyObject *self, PyObject *arg)
{
    Py_ssize_t pathSize;
    const char *path = PyUnicode_AsUTF8AndSize(arg, &pathSize);
    if (unlikely(path == NULL))
    {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS;

    size_t sizeToAlloc = sizeof(DROPFILES) + pathSize + 2;

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

    if (!set_win_clipboard(CF_HDROP, hGlobal))
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
    CMemoryViewBuffer *memoryViewBuffer = (CMemoryViewBuffer *)arg;
    unsigned long remainingBytesToEncode = memoryViewBuffer->bufferSize;
    char *originalBufferPosition = memoryViewBuffer->buffer;

    Py_BEGIN_ALLOW_THREADS;

    // encoded data is ~4/3x the size of the original data so make encoded buffer 2x the size.
    HGLOBAL hGlobal = GlobalAlloc(GHND, 2 * remainingBytesToEncode);
    if (unlikely(hGlobal == NULL))
    {
        goto end;
    }

    base64_encodestate state;
    char *encodedBuffer = (char *)GlobalLock(hGlobal);
    char *encodedBufferPosition = encodedBuffer;

    if (unlikely(encodedBuffer == NULL))
    {
        GlobalFree(hGlobal);
        goto end;
    }

    base64_init_encodestate(&state);

    const unsigned long MAX_BYTES_TO_ENCODE_AT_ONCE = 1048576;
    while (remainingBytesToEncode > 0)
    {
        unsigned bytesToEncode = (unsigned)(remainingBytesToEncode < MAX_BYTES_TO_ENCODE_AT_ONCE ? remainingBytesToEncode : MAX_BYTES_TO_ENCODE_AT_ONCE);

        encodedBufferPosition += base64_encode_block(originalBufferPosition, bytesToEncode, encodedBufferPosition, &state);
        remainingBytesToEncode -= bytesToEncode;
        originalBufferPosition += bytesToEncode;
    }

    base64_encode_blockend(encodedBuffer, &state);

    GlobalUnlock(hGlobal);

    set_win_clipboard(CF_TEXT, encodedBuffer);

end:
    Py_END_ALLOW_THREADS;
    return Py_None;
}

static PyMethodDef os_methods[] = {
    {"set_hwnd", set_hwnd, METH_O, NULL},
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
