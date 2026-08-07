#include "includes/base64.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

int main() {

    unsigned long input_size = 4194304;
    char *random_input = malloc(sizeof(char) * input_size);
    memset(random_input, 'a', input_size - 1);
    char *buffer = malloc(sizeof(char) * input_size * 2);

    clock_t begin = clock();

    base64_encode(random_input, input_size, buffer);

    clock_t end = clock();
    double seconds = (double)(end - begin) / CLOCKS_PER_SEC;

    printf("Base64 encode took %f seconds\n", seconds);

    return 0;
}
