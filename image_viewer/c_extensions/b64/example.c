#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>

void avx2_base64_encode(const uint8_t *src, size_t srclen, char *dst) {
    size_t i = 0;
    size_t dst_len = 0;

    // Process 24 input bytes -> 32 output bytes per iteration
    for (; i + 24 <= srclen; i += 24, dst_len += 32) {
        // 1. Load 24 bytes from source (pad with zeros up to 32 bytes for register fill)
        __m256i input = _mm256_loadu_si256((const __m256i *)(src + i));

        // 2. Shuffle bytes to align 3-byte groups inside 4-byte fields
        // Source pattern: [A, B, C, D, E, F...] -> Target pattern: [A, B, C, B, D, E, F, E...]
        __m256i shuffle_mask = _mm256_setr_epi8(
            0, 1, 2, 1, 3, 4, 5, 4, 6, 7, 8, 7, 9, 10, 11, 10, 12, 13, 14, 13, 15, 16, 17, 16, 18, 19, 20, 19, 21, 22, 23, 22
        );
        __m256i expanded = _mm256_shuffle_epi8(input, shuffle_mask);

        // 3. Isolate the target 6-bit spaces using shifting masks
        __m256i mask_0 = _mm256_set1_epi32(0xFC000000); // Top 6 bits of byte 0
        __m256i mask_1 = _mm256_set1_epi32(0x00FC0000); // Top 6 bits of byte 1
        __m256i mask_2 = _mm256_set1_epi32(0x0000FC00); // Top 6 bits of byte 2
        __m256i mask_3 = _mm256_set1_epi32(0x000000FC); // Top 6 bits of byte 3

        // Group shift values within 32-bit lanes to align bits down to lower bounds
        __m256i b0 = _mm256_srli_epi32(_mm256_and_si256(expanded, mask_0), 26);
        __m256i b1 = _mm256_srli_epi32(_mm256_and_si256(expanded, mask_1), 12);
        __m256i b2 = _mm256_slli_epi32(_mm256_and_si256(expanded, mask_2), 2);
        __m256i b3 = _mm256_slli_epi32(_mm256_and_si256(expanded, mask_3), 16);

        // Combine fields back into a single vector of 6-bit values (indices 0-63)
        __m256i indices = _mm256_or_si256(_mm256_or_si256(b0, b1), _mm256_or_si256(b2, b3));

        // 4. Vectorized Translate indices to ASCII characters
        // Ranges: 'A'-'Z' (0-25), 'a'-'z' (26-51), '0'-'9' (52-61), '+' (62), '/' (63)

        // Form masks for character subsets
        __m256i lt_26 = _mm256_cmpgt_epi8(_mm256_set1_epi8(26), indices);
        __m256i lt_52 = _mm256_andnot_si256(lt_26, _mm256_cmpgt_epi8(_mm256_set1_epi8(52), indices));
        __m256i lt_62 = _mm256_andnot_si256(_mm256_cmpgt_epi8(_mm256_set1_epi8(52), indices),
                                            _mm256_cmpgt_epi8(_mm256_set1_epi8(62), indices));
        __m256i eq_62 = _mm256_cmpeq_epi8(indices, _mm256_set1_epi8(62));
        __m256i eq_63 = _mm256_cmpeq_epi8(indices, _mm256_set1_epi8(63));

        // Apply constant offsets to convert indices straight to ASCII values
        __m256i result = _mm256_setzero_si256();
        result = _mm256_or_si256(result, _mm256_and_si256(lt_26, _mm256_add_epi8(indices, _mm256_set1_epi8('A'))));
        result = _mm256_or_si256(result, _mm256_and_si256(lt_52, _mm256_add_epi8(indices, _mm256_set1_epi8('a' - 26))));
        result = _mm256_or_si256(result, _mm256_and_si256(lt_62, _mm256_add_epi8(indices, _mm256_set1_epi8('0' - 52))));
        result = _mm256_or_si256(result, _mm256_and_si256(eq_62, _mm256_set1_epi8('+')));
        result = _mm256_or_si256(result, _mm256_and_si256(eq_63, _mm256_set1_epi8('/')));

        // 5. Stream output directly to destination buffer
        _mm256_storeu_si256((__m256i *)(dst + dst_len), result);
    }

    // Scalar Fallback Tail: Handle remaining 1 to 23 trailing source bytes
    static const char b64_table[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    while (i < srclen) {
        uint32_t val = src[i++] << 16;
        int remaining = 1;

        if (i < srclen) {
            val |= src[i++] << 8;
            remaining++;
        }
        if (i < srclen) {
            val |= src[i++];
            remaining++;
        }

        dst[dst_len++] = b64_table[(val >> 18) & 0x3F];
        dst[dst_len++] = b64_table[(val >> 12) & 0x3F];
        dst[dst_len++] = (remaining > 1) ? b64_table[(val >> 6) & 0x3F] : '=';
        dst[dst_len++] = (remaining > 2) ? b64_table[val & 0x3F] : '=';
    }
    dst[dst_len] = '\0'; // Null-terminate string
}
