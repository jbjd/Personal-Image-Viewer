#include "includes/base64.h"

static char _base64_encode_char(char to_encode) {
    static const char *encoding = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    if (to_encode > 63) {
        return '=';
    }
    return encoding[(int)to_encode];
}

void base64_encode(const char *input, unsigned int input_size, char *encoded_out) {
    const char *input_position = input;
    const char *const input_end = input + input_size;

    char *output_position = encoded_out;
    char fragment;

    char result = 0;

    while (1) {
        if (input_position == input_end) {
            goto end;
        }
        fragment = *input_position++;
        result = (fragment & 0x0fc) >> 2;
        *output_position++ = _base64_encode_char(result);
        result = (fragment & 0x003) << 4;

        if (input_position == input_end) {
            *output_position++ = _base64_encode_char(result);
            *output_position++ = '=';
            *output_position++ = '=';
            goto end;
        }
        fragment = *input_position++;
        result |= (fragment & 0x0f0) >> 4;
        *output_position++ = _base64_encode_char(result);
        result = (fragment & 0x00f) << 2;

        if (input_position == input_end) {
            *output_position++ = _base64_encode_char(result);
            *output_position++ = '=';
            goto end;
        }
        fragment = *input_position++;
        result |= (fragment & 0x0c0) >> 6;
        *output_position++ = _base64_encode_char(result);
        result = fragment & 0x03f;
        *output_position++ = _base64_encode_char(result);
    }

end:
    *output_position = '\0';
}
