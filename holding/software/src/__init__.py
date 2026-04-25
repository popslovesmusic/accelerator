"""Level 2 1D NOT-axiom simulation package."""

from .native_backend import (
    is_native_backend_available,
    native_backend_name,
    native_backend_max_threads,
    set_native_backend_threads,
)

__all__ = [
    "is_native_backend_available",
    "native_backend_name",
    "native_backend_max_threads",
    "set_native_backend_threads",
]
