#ifndef PIV_CONFIG_DEFAULTS
#define PIV_CONFIG_DEFAULTS

const char *KEY_CACHE_SIZE = "SIZE";
const char *KEY_KB_COPY_TO_CLIPBOARD_AS_BASE64 = "COPY_TO_CLIPBOARD_AS_BASE64";
const char *KEY_KB_MOVE_TO_NEW_FILE = "MOVE_TO_NEW_FILE";
const char *KEY_KB_OPTIMIZE_IMAGE = "OPTIMIZE_IMAGE";
const char *KEY_KB_REFRESH = "REFRESH";
const char *KEY_KB_RELOAD_IMAGE = "RELOAD_IMAGE";
const char *KEY_KB_RENAME = "RENAME";
const char *KEY_KB_SHOW_DETAILS = "SHOW_DETAILS";
const char *KEY_KB_UNDO_MOST_RECENT_ACTION = "UNDO_MOST_RECENT_ACTION";
const char *KEY_UI_BACKGROUND_COLOR = "BACKGROUND_COLOR";
const char *KEY_UI_FONT = "FONT";

const int DEFAULT_CACHE_SIZE = 20;
const char *DEFAULT_KB_COPY_TO_CLIPBOARD_AS_BASE64 = "<Control-E>";
const char *DEFAULT_KB_MOVE_TO_NEW_FILE = "<Control-m>";
const char *DEFAULT_KB_OPTIMIZE_IMAGE = "<Control-o>";
const char *DEFAULT_KB_REFRESH = "<Control-r>";
const char *DEFAULT_KB_RELOAD_IMAGE = "<F5>";
const char *DEFAULT_KB_RENAME = "<F2>";
const char *DEFAULT_KB_SHOW_DETAILS = "<Control-d>";
const char *DEFAULT_KB_UNDO_MOST_RECENT_ACTION = "<Control-z>";
const char *DEFAULT_UI_BACKGROUND_COLOR = "#000000";

#ifdef _WIN32
const char *DEFAULT_UI_FONT = "arial.ttf";
#else
const char *DEFAULT_UI_FONT = "LiberationSans-Regular.ttf";
#endif

#endif /* PIV_CONFIG_DEFAULTS */
