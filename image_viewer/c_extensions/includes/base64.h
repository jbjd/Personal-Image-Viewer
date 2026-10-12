#ifndef PIV_BASE64
#define PIV_BASE64

unsigned long long get_safe_buffer_size_for_base64_encode(unsigned long input_size);

void base64_encode(const char *input, unsigned int input_size, char *encoded_out);

#endif /* PIV_BASE64 */
