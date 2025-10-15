"""
Test suite for Sutra Storage Python bindings
"""
import numpy as np
import sutra_storage


def test_basic_initialization():
    """Test creating a new store"""
    store = sutra_storage.GraphStore("/tmp/test_sutra_storage")
    stats = store.stats()
    assert stats['total_vectors'] == 0
    assert stats['dimension'] == 384
    print("✓ Basic initialization works")


def test_vector_operations():
    """Test adding and retrieving vectors"""
    store = sutra_storage.GraphStore("/tmp/test_sutra_vectors", vector_dimension=128)
    
    # Create test vectors
    vec1 = np.random.rand(128).astype(np.float32)
    vec2 = np.random.rand(128).astype(np.float32)
    
    # Add vectors
    store.add_vector("a" * 32, vec1)  # 32-char hex ID
    store.add_vector("b" * 32, vec2)
    
    # Retrieve vectors
    retrieved1 = store.get_vector("a" * 32)
    assert retrieved1 is not None
    assert np.allclose(retrieved1, vec1)
    
    # Check stats
    stats = store.stats()
    assert stats['total_vectors'] == 2
    
    print("✓ Vector operations work")


def test_distance_computation():
    """Test distance calculations"""
    store = sutra_storage.GraphStore("/tmp/test_distances", vector_dimension=64)
    
    # Create orthogonal vectors
    vec1 = np.zeros(64, dtype=np.float32)
    vec1[0] = 1.0
    
    vec2 = np.zeros(64, dtype=np.float32)
    vec2[1] = 1.0
    
    store.add_vector("c" * 32, vec1)
    store.add_vector("d" * 32, vec2)
    
    # Compute distance
    dist = store.distance("c" * 32, "d" * 32)
    assert 0 <= dist <= 2.0  # Cosine distance range
    
    print(f"✓ Distance computation works (distance={dist:.4f})")


def test_index_operations():
    """Test graph indexing"""
    store = sutra_storage.GraphStore("/tmp/test_index")
    
    # Add associations (use valid hex IDs)
    store.add_association("e" * 32, "f" * 32)
    store.add_association("e" * 32, "a" * 32)
    
    # Get neighbors
    neighbors = store.get_neighbors("e" * 32)
    assert len(neighbors) == 2
    
    stats = store.stats()
    assert stats['total_edges'] == 2
    
    print("✓ Index operations work")


def test_context_manager():
    """Test using store as context manager"""
    with sutra_storage.GraphStore("/tmp/test_context") as store:
        vec = np.random.rand(384).astype(np.float32)
        store.add_vector("0" * 32, vec)
        stats = store.stats()
        assert stats['total_vectors'] == 1
    
    print("✓ Context manager works")


def test_quantization():
    """Test vector quantization training"""
    store = sutra_storage.GraphStore("/tmp/test_quantization", vector_dimension=128, use_compression=True)
    
    # Generate training vectors (need more than num_centroids=256)
    training_vecs = [np.random.rand(128).astype(np.float32) for _ in range(300)]
    
    # Add vectors to store
    for i, vec in enumerate(training_vecs):
        hex_id = f"{i:032x}"  # Convert number to 32-char hex
        store.add_vector(hex_id, vec)
    
    # Train quantizer
    store.train_quantizer(training_vecs)
    
    stats = store.stats()
    assert stats['quantizer_trained'] == True
    assert stats['total_vectors'] == 300
    
    print("✓ Quantization training works")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Sutra Storage Python Bindings Test Suite")
    print("="*60 + "\n")
    
    test_basic_initialization()
    test_vector_operations()
    test_distance_computation()
    test_index_operations()
    test_context_manager()
    test_quantization()
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60 + "\n")
