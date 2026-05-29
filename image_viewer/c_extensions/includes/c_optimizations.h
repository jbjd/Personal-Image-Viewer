#define unlikely(x) __builtin_expect(!!(x), 0)
#define VARIABLE_NAME(Variable) (#Variable)
