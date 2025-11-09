import numpy as np
import time
from pathlib import Path
import pytest

integration = pytest.mark.integration

# RustStorageAdapter removed - all tests use TcpStorageAdapter now
# These tests are for local mode only (not production)
RUST_AVAILABLE = False

try:
    from sutra_core.graph.concepts import Concept, Association, AssociationType
except Exception:
    pass


@integration
@pytest.mark.skipif(not RUST_AVAILABLE, reason="RustStorageAdapter removed - use TCP mode")
def test_association_neighbors(tmp_path: Path):
    pytest.skip("RustStorageAdapter removed - use TCP mode")


@integration
@pytest.mark.skipif(not RUST_AVAILABLE, reason="RustStorageAdapter removed - use TCP mode")
def test_find_paths_chain(tmp_path: Path):
    pytest.skip("RustStorageAdapter removed - use TCP mode")
