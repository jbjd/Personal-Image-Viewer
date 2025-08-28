# Compilation Notes

## Unusable GCC Flags (Nuitka)

Assume -O3

* -Ofast (Unsafe in multi-threaded context)
* -fallow-store-data-races (Unsafe in multi-threaded context)
