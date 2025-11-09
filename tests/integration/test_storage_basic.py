import os
import numpy as np
import time
from pathlib import Path
import pytest

integration = pytest.mark.integration

# RustStorageAdapter removed - all tests use TcpStorageAdapter now
# These tests are for local mode only (not production)
RUST_AVAILABLE = False


@integration
@pytest.mark.skipif(not RUST_AVAILABLE, reason="RustStorageAdapter removed - use TCP mode")
def test_storage_learn_and_search_smoke(tmp_path: Path):
    # Test skipped - RustStorageAdapter removed
    # Use TcpStorageAdapter with storage server instead
    pytest.skip("RustStorageAdapter removed - use TCP mode")
