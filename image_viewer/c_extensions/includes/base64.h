#ifndef PIV_BASE64
#define PIV_BASE64

void base64_encode(const char *input, unsigned int input_size, char *encoded_out);

void base64_encode_avx2(const char *input, unsigned int input_size, char *encoded_out);

#endif /* PIV_BASE64 */
