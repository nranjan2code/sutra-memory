"""
Sutra storage (Rust-backed only).

This package exposes only the RustStorageAdapter and intentionally drops
all legacy Python storage implementations and JSON persistence.
"""

from .rust_adapter import RustStorageAdapter

__all__ = ["RustStorageAdapter"]
