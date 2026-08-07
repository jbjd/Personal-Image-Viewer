#include "includes/base64.h"

static char _base64_encode_char(char to_encode) {
    static const char *base64_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    return base64_alphabet[(int)to_encode];
}

void base64_encode(const char *input, unsigned int input_size, char *encoded_out) {
    const char *input_position = input;
    const char *const input_end = input + input_size;
    char current_char;
    char *output_position = encoded_out;

    while (1) {
        if (input_position == input_end) {
            break;
        }
        current_char = *input_position++;
        char fragment = (current_char & 0x0fc) >> 2;
        *output_position++ = _base64_encode_char(fragment);
        fragment = (current_char & 0x003) << 4;

        if (input_position == input_end) {
            *output_position++ = _base64_encode_char(fragment);
            *output_position++ = '=';
            *output_position++ = '=';
            break;
        }
        current_char = *input_position++;
        fragment |= (current_char & 0x0f0) >> 4;
        *output_position++ = _base64_encode_char(fragment);
        fragment = (current_char & 0x00f) << 2;

        if (input_position == input_end) {
            *output_position++ = _base64_encode_char(fragment);
            *output_position++ = '=';
            break;
        }
        current_char = *input_position++;
        fragment |= (current_char & 0x0c0) >> 6;
        *output_position++ = _base64_encode_char(fragment);
        fragment = current_char & 0x03f;
        *output_position++ = _base64_encode_char(fragment);
    }

    *output_position = '\0';
}
