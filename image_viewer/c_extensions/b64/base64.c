#include "includes/base64.h"

static char _base64_encode_char(char to_encode) {
    static const char *base64_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    return base64_alphabet[(int)to_encode];
}

static inline void _base64_encode(const char *input, unsigned int input_size, char *encoded_out) {
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

#ifdef __AVX2__

#include <immintrin.h>

static inline void _base64_encode_avx2(const char *input, unsigned int input_size, char *encoded_out) {
    unsigned int i = 0;
    for (; i + 32 <= input_size; i += 24, encoded_out += 32) {

        // Load 32 bytes from input, but only 24 will be used
        __m256i load = _mm256_loadu_si256((const __m256i *)(input + i));

        // [a, b, c, d, e, f, ...] -> [a, b, b, c, d, e, e, f, ...]
        __m256i shuffle_mask = _mm256_setr_epi8(
            0, 1, 1, 2, 3, 4, 4, 5, 6, 7, 7, 8, 9, 10, 10, 11, 12, 13, 13, 14, 15, 16, 16, 17, 18, 19, 19, 20, 21, 22, 22, 23
        );
        __m256i shuffled = _mm256_shuffle_epi8(load, shuffle_mask);

        // Get 6 bit masks and turn into 4 bytes in range 0-63 each
        __m256i mask_0 = _mm256_set1_epi32(0xFC000000);
        __m256i mask_1 = _mm256_set1_epi32(0x03F00000);
        __m256i mask_2 = _mm256_set1_epi32(0x00000FC0);
        __m256i mask_3 = _mm256_set1_epi32(0x0000003F);

        // For some reason, I need to effectively swap the order of the bytes
        __m256i pre_encoded_byte_0 = _mm256_srli_epi32(_mm256_and_si256(shuffled, mask_0), 26);
        __m256i pre_encoded_byte_1 = _mm256_srli_epi32(_mm256_and_si256(shuffled, mask_1), 12);
        __m256i pre_encoded_byte_2 = _mm256_slli_epi32(_mm256_and_si256(shuffled, mask_2), 10);
        __m256i pre_encoded_byte_3 = _mm256_slli_epi32(_mm256_and_si256(shuffled, mask_3), 24);

        __m256i pre_encoded_bytes_packed = _mm256_or_si256(
            _mm256_or_si256(pre_encoded_byte_0, pre_encoded_byte_1),
            _mm256_or_si256(pre_encoded_byte_2, pre_encoded_byte_3)
        );

        // Now need to turn bytes values into base64
        // Values 0-25  are A-Z
        // Values 26-51 are a-z
        // Values 52-61 are 0-9
        // Value 62 is +
        // Value 63 is /

        // _mm256_cmpgt_epi8 will fill byte with 0xFF if true, 0x00 if false
        __m256i is_az_case_insensitive = _mm256_cmpgt_epi8(_mm256_set1_epi8(52), pre_encoded_bytes_packed);

        __m256i is_AZ = _mm256_cmpgt_epi8(_mm256_set1_epi8(26), pre_encoded_bytes_packed);
        __m256i is_az = _mm256_andnot_si256(is_AZ, is_az_case_insensitive);
        __m256i is_09 = _mm256_andnot_si256(
            is_az_case_insensitive,
            _mm256_cmpgt_epi8(_mm256_set1_epi8(62), pre_encoded_bytes_packed)
        );
        __m256i is_plus = _mm256_cmpeq_epi8(_mm256_set1_epi8(62), pre_encoded_bytes_packed);
        __m256i is_slash = _mm256_cmpeq_epi8(_mm256_set1_epi8(63), pre_encoded_bytes_packed);

        __m256i result = _mm256_setzero_si256();
        result = _mm256_or_si256(result, _mm256_and_si256(is_AZ, _mm256_add_epi8(pre_encoded_bytes_packed, _mm256_set1_epi8('A'))));
        result = _mm256_or_si256(result, _mm256_and_si256(is_az, _mm256_add_epi8(pre_encoded_bytes_packed, _mm256_set1_epi8('a' - 26))));
        result = _mm256_or_si256(result, _mm256_and_si256(is_09, _mm256_add_epi8(pre_encoded_bytes_packed, _mm256_set1_epi8('0' - 52))));
        result = _mm256_or_si256(result, _mm256_and_si256(is_plus, _mm256_set1_epi8('+')));
        result = _mm256_or_si256(result, _mm256_and_si256(is_slash, _mm256_set1_epi8('/')));

        _mm256_storeu_si256((__m256i *)encoded_out, result);
    }

    _base64_encode(input + i, input_size - i, encoded_out);
}

#endif /* __AVX2__ */

#ifdef __AVX2__
#define base64_encode_inner _base64_encode_avx2
#else
#define base64_encode_inner _base64_encode
#endif /* __AVX2__ */

void base64_encode(const char *input, unsigned int input_size, char *encoded_out) {
    base64_encode_inner(input, input_size, encoded_out);
}
