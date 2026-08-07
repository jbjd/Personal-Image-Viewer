#include "util.h"

CU_ErrorCode CU_EXT_cleanup() {
    CU_cleanup_registry();
    return CU_get_error();
}

CU_ErrorCode CU_EXT_run_and_cleanup() {
    CU_basic_set_mode(CU_BRM_SILENT);
    CU_basic_run_tests();
    return CU_EXT_cleanup();
}
