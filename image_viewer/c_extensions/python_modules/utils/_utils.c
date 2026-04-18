#include "b64/cencode.h"

#include "_utils.h"

void encode_buffer_base64(char *buffer, unsigned long buffer_size, char *encoded_buffer_out)
{
    base64_encodestate state;
    base64_init_encodestate(&state);

    char *encoded_buffer_position = encoded_buffer_out;

    const unsigned long MAX_BYTES_TO_ENCODE_AT_ONCE = 1048576;
    while (buffer_size > 0)
    {
        unsigned byte_to_encode_this_iteration = (unsigned)(buffer_size < MAX_BYTES_TO_ENCODE_AT_ONCE ? buffer_size : MAX_BYTES_TO_ENCODE_AT_ONCE);

        encoded_buffer_position += base64_encode_block(buffer, byte_to_encode_this_iteration, encoded_buffer_position, &state);
        buffer_size -= byte_to_encode_this_iteration;
        buffer += byte_to_encode_this_iteration;
    }

    base64_encode_blockend(encoded_buffer_out, &state);
}
