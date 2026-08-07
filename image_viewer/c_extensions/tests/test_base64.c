#include "includes/base64.h"
#include "tests/util.h"

#include <CUnit/Basic.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static inline void _run_base64_encode_assert_expected(const char *input, const char *expected, char *buffer) {
    printf("\nRunning base64 encode on %s\n", input);

    base64_encode(input, strlen(input), buffer);

    if (strcmp(buffer, expected) != 0) {
        printf("Failed\nExpected: %s\nActual: %s\n", expected, buffer);
        CU_FAIL();
    } else {
        puts("Passed");
        CU_PASS();
    }
}

void test_encoding() {
    char *buffer = malloc(sizeof(char) * 64);

    _run_base64_encode_assert_expected("a", "YQ==", buffer);
    _run_base64_encode_assert_expected("aa", "YWE=", buffer);
    _run_base64_encode_assert_expected("aaa", "YWFh", buffer);
    _run_base64_encode_assert_expected(">>>???aaaAAAaaaaaaaaaaaaaaaaaaaaaa", "Pj4+Pz8/YWFhQUFBYWFhYWFhYWFhYWFhYWFhYWFhYWFhYQ==", buffer);

    free(buffer);
}

int init_suite(void) {
    return 0;
}

int clean_suite(void) {
    return 0;
}

int main(int argc, char *argv[]) {
    CU_pSuite suite = NULL;

    if (CUE_SUCCESS != CU_initialize_registry()) {
        return CU_get_error();
    }

    suite = CU_add_suite("Base64", init_suite, clean_suite);
    if (NULL == suite) {
        return CU_EXT_cleanup();
    }

    if (NULL == CU_add_test(suite, "Encode", test_encoding)) {
        return CU_EXT_cleanup();
    }

    return CU_EXT_run_and_cleanup();
}
