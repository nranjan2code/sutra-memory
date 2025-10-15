"""
Storage backend for Sutra AI system.

Provides direct integration with Rust storage engine:
- RustStorageAdapter: High-performance storage (vectors + graph + metadata)

No backward compatibility needed - forward-looking only.
"""

# RustStorageAdapter imported conditionally (requires compiled extension)
try:
    from .rust_adapter import RustStorageAdapter
    __all__ = ["RustStorageAdapter"]
except ImportError as e:
    # Rust storage not available (extension not built)
    import warnings
    warnings.warn(
        f"Rust storage not available: {e}. "
        "Build with: cd packages/sutra-storage && maturin develop"
    )
    __all__ = []
