/// Python bindings for Sutra Storage Engine
/// 
/// Provides a Pythonic interface to the high-performance Rust storage backend.
use pyo3::prelude::*;
use pyo3::exceptions::{PyException, PyValueError, PyIOError};
use pyo3::types::{PyDict, PyList};
use numpy::{PyArray1, PyReadonlyArray1};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

use crate::types::{ConceptId, AssociationId, ConceptRecord, AssociationRecord, AssociationType};
use crate::lsm::LSMTree;
use crate::index::GraphIndex;
use crate::vectors::{VectorStore, VectorConfig};
use crate::wal::WriteAheadLog;

// =============================================================================
// Error Conversion
// =============================================================================

/// Custom error type for Python
#[derive(Debug)]
struct StorageError(String);

impl std::fmt::Display for StorageError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl std::error::Error for StorageError {}

impl From<StorageError> for PyErr {
    fn from(err: StorageError) -> PyErr {
        PyException::new_err(err.0)
    }
}

impl From<std::io::Error> for StorageError {
    fn from(err: std::io::Error) -> StorageError {
        StorageError(format!("IO error: {}", err))
    }
}

impl From<anyhow::Error> for StorageError {
    fn from(err: anyhow::Error) -> StorageError {
        StorageError(format!("Storage error: {}", err))
    }
}

// =============================================================================
// Python-facing Types
// =============================================================================

/// Python wrapper for ConceptId
#[pyclass(name = "ConceptId")]
#[derive(Clone)]
struct PyConceptId {
    inner: ConceptId,
}

#[pymethods]
impl PyConceptId {
    #[new]
    fn new(hex_id: &str) -> PyResult<Self> {
        Ok(Self {
            inner: ConceptId::from_string(hex_id),
        })
    }
    
    fn __str__(&self) -> String {
        self.inner.to_hex()
    }
    
    fn __repr__(&self) -> String {
        format!("ConceptId('{}')", self.inner.to_hex())
    }
    
    fn __hash__(&self) -> u64 {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        let mut hasher = DefaultHasher::new();
        self.inner.hash(&mut hasher);
        hasher.finish()
    }
    
    fn __eq__(&self, other: &PyConceptId) -> bool {
        self.inner == other.inner
    }
}

/// Python wrapper for concept data
#[pyclass(name = "Concept")]
#[derive(Clone)]
struct PyConcept {
    #[pyo3(get, set)]
    id: String,
    
    #[pyo3(get, set)]
    content: String,
    
    #[pyo3(get, set)]
    strength: f32,
    
    #[pyo3(get, set)]
    confidence: f32,
    
    #[pyo3(get, set)]
    access_count: u32,
    
    #[pyo3(get, set)]
    created: u64,
    
    #[pyo3(get, set)]
    last_accessed: u64,
}

#[pymethods]
impl PyConcept {
    fn __repr__(&self) -> String {
        format!("Concept(id='{}', content='{}')", self.id, self.content)
    }
    
    /// Convert to Python dictionary
    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("id", &self.id)?;
        dict.set_item("content", &self.content)?;
        dict.set_item("strength", self.strength)?;
        dict.set_item("confidence", self.confidence)?;
        dict.set_item("access_count", self.access_count)?;
        dict.set_item("created", self.created)?;
        dict.set_item("last_accessed", self.last_accessed)?;
        Ok(dict.into())
    }
}

/// Python wrapper for association data
#[pyclass(name = "Association")]
#[derive(Clone)]
struct PyAssociation {
    #[pyo3(get, set)]
    id: u64,
    
    #[pyo3(get, set)]
    source: String,
    
    #[pyo3(get, set)]
    target: String,
    
    #[pyo3(get, set)]
    strength: f32,
    
    #[pyo3(get, set)]
    assoc_type: u8,
}

#[pymethods]
impl PyAssociation {
    fn __repr__(&self) -> String {
        format!("Association(source='{}', target='{}')", self.source, self.target)
    }
    
    /// Convert to Python dictionary
    fn to_dict(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        dict.set_item("id", self.id)?;
        dict.set_item("source", &self.source)?;
        dict.set_item("target", &self.target)?;
        dict.set_item("strength", self.strength)?;
        dict.set_item("type", self.assoc_type)?;
        Ok(dict.into())
    }
}

// =============================================================================
// Transaction Context Manager
// =============================================================================

/// Transaction context for ACID operations
#[pyclass(name = "Transaction")]
struct PyTransaction {
    transaction_id: Option<u64>,
    committed: bool,
    store: Py<PyGraphStore>,
}

#[pymethods]
impl PyTransaction {
    fn __enter__(mut slf: PyRefMut<'_, Self>) -> PyResult<PyRefMut<'_, Self>> {
        // Begin transaction
        let py = slf.py();
        let store = slf.store.borrow(py);
        let tx_id = store.begin_transaction()?;
        slf.transaction_id = Some(tx_id);
        slf.committed = false;
        Ok(slf)
    }
    
    fn __exit__(
        &mut self,
        py: Python,
        _exc_type: PyObject,
        _exc_value: PyObject,
        _traceback: PyObject,
    ) -> PyResult<bool> {
        if let Some(tx_id) = self.transaction_id {
            let store = self.store.borrow(py);
            
            // If not committed, rollback
            if !self.committed {
                store.rollback_transaction(tx_id)?;
            }
        }
        Ok(false)  // Don't suppress exceptions
    }
    
    /// Commit the transaction
    fn commit(&mut self, py: Python) -> PyResult<()> {
        if let Some(tx_id) = self.transaction_id {
            let store = self.store.borrow(py);
            store.commit_transaction(tx_id)?;
            self.committed = true;
        }
        Ok(())
    }
    
    /// Rollback the transaction
    fn rollback(&mut self, py: Python) -> PyResult<()> {
        if let Some(tx_id) = self.transaction_id {
            let store = self.store.borrow(py);
            store.rollback_transaction(tx_id)?;
            self.committed = true;  // Mark as handled
        }
        Ok(())
    }
}

// =============================================================================
// Main GraphStore Python Wrapper
// =============================================================================

/// High-level Python interface to the storage engine
#[pyclass(name = "GraphStore")]
struct PyGraphStore {
    lsm: Arc<Mutex<LSMTree>>,
    index: Arc<Mutex<GraphIndex>>,
    vectors: Arc<Mutex<VectorStore>>,
    wal: Arc<Mutex<WriteAheadLog>>,
    path: PathBuf,
}

#[pymethods]
impl PyGraphStore {
    #[new]
    #[pyo3(signature = (path, vector_dimension=384, use_compression=true))]
    fn new(
        path: &str,
        vector_dimension: usize,
        use_compression: bool,
    ) -> PyResult<Self> {
        let path_buf = PathBuf::from(path);
        
        // Create directory if it doesn't exist
        std::fs::create_dir_all(&path_buf)
            .map_err(|e| StorageError(format!("Failed to create directory: {}", e)))?;
        
        // Initialize LSM-Tree
        let lsm = Arc::new(Mutex::new(
            LSMTree::open(&path_buf)
                .map_err(|e| StorageError(format!("Failed to open LSM tree: {}", e)))?
        ));
        
        // Initialize indexes
        let index = Arc::new(Mutex::new(GraphIndex::new()));
        
        // Initialize vector store
        let vector_config = VectorConfig {
            dimension: vector_dimension,
            use_compression,
            num_subvectors: vector_dimension / 8,  // 8 dims per subvector
            num_centroids: 256,
        };
        
        let vectors = Arc::new(Mutex::new(
            VectorStore::new(path_buf.join("vectors"), vector_config)
                .map_err(|e| StorageError(format!("Failed to create vector store: {}", e)))?
        ));
        
        // Initialize WAL
        let wal = Arc::new(Mutex::new(
            WriteAheadLog::open(path_buf.join("wal.log"))
                .map_err(|e| StorageError(format!("Failed to open WAL: {}", e)))?
        ));
        
        Ok(Self {
            lsm,
            index,
            vectors,
            wal,
            path: path_buf,
        })
    }
    
    /// Open existing store and replay WAL
    #[staticmethod]
    fn open(path: &str) -> PyResult<Self> {
        let path_buf = PathBuf::from(path);
        
        if !path_buf.exists() {
            return Err(StorageError(format!("Store does not exist: {}", path)).into());
        }
        
        // Open LSM-Tree
        let lsm = Arc::new(Mutex::new(
            LSMTree::open(&path_buf)
                .map_err(|e| StorageError(format!("Failed to open LSM tree: {}", e)))?
        ));
        
        // Open vector store
        let vectors = Arc::new(Mutex::new(
            VectorStore::load(path_buf.join("vectors"))
                .map_err(|e| StorageError(format!("Failed to load vector store: {}", e)))?
        ));
        
        // Open WAL
        let wal = Arc::new(Mutex::new(
            WriteAheadLog::open(path_buf.join("wal.log"))
                .map_err(|e| StorageError(format!("Failed to open WAL: {}", e)))?
        ));
        
        // Create indexes
        let index = Arc::new(Mutex::new(GraphIndex::new()));
        
        // TODO: Replay WAL and rebuild indexes
        
        Ok(Self {
            lsm,
            index,
            vectors,
            wal,
            path: path_buf,
        })
    }
    
    // -------------------------------------------------------------------------
    // Concept Operations
    // -------------------------------------------------------------------------
    
    /// Add or update a concept
    #[pyo3(signature = (concept_id, content, vector=None, strength=1.0, confidence=1.0))]
    fn add_concept(
        &self,
        concept_id: &str,
        content: &str,
        vector: Option<PyReadonlyArray1<f32>>,
        strength: f32,
        confidence: f32,
    ) -> PyResult<()> {
        let id = ConceptId::from_string(concept_id);
        
        // Add vector if provided
        if let Some(vec_array) = vector {
            let vec = vec_array.as_slice()?.to_vec();
            self.vectors.add_vector(id, vec)
                .map_err(|e| StorageError(format!("Failed to add vector: {}", e)))?;
        }
        
        // TODO: Write to LSM and WAL
        // For now, just add to index
        
        Ok(())
    }
    
    /// Get a concept by ID
    fn get_concept(&self, concept_id: &str) -> PyResult<Option<PyConcept>> {
        let id = ConceptId::from_string(concept_id);
        
        // TODO: Read from LSM using index
        // For now, return None
        
        Ok(None)
    }
    
    /// Check if concept exists
    fn has_concept(&self, concept_id: &str) -> PyResult<bool> {
        let id = ConceptId::from_string(concept_id);
        Ok(self.index.get_concept_location(&id).is_some())
    }
    
    /// Remove a concept
    fn remove_concept(&self, concept_id: &str) -> PyResult<()> {
        let id = ConceptId::from_string(concept_id);
        
        // Remove vector
        self.vectors.remove_vector(&id)
            .map_err(|e| StorageError(format!("Failed to remove vector: {}", e)))?;
        
        // TODO: Write tombstone to LSM and WAL
        
        Ok(())
    }
    
    /// Get all concept IDs
    fn list_concepts(&self, py: Python) -> PyResult<PyObject> {
        let ids: Vec<String> = self.index.get_all_concept_ids()
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, ids).into())
    }
    
    // -------------------------------------------------------------------------
    // Association Operations
    // -------------------------------------------------------------------------
    
    /// Add an association between concepts
    #[pyo3(signature = (source_id, target_id, strength=1.0, assoc_type=0))]
    fn add_association(
        &self,
        source_id: &str,
        target_id: &str,
        strength: f32,
        assoc_type: u8,
    ) -> PyResult<u64> {
        let source = ConceptId::from_string(source_id);
        let target = ConceptId::from_string(target_id);
        
        // Add to adjacency index
        self.index.add_association(&source, &target);
        
        // TODO: Write to LSM and WAL
        
        Ok(0)  // Return association ID
    }
    
    /// Get neighbors of a concept
    fn get_neighbors(&self, concept_id: &str, py: Python) -> PyResult<PyObject> {
        let id = ConceptId::from_string(concept_id);
        
        let neighbors: Vec<String> = self.index.get_neighbors(&id)
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, neighbors).into())
    }
    
    // -------------------------------------------------------------------------
    // Vector Operations
    // -------------------------------------------------------------------------
    
    /// Add a vector for a concept
    fn add_vector<'py>(
        &self,
        concept_id: &str,
        vector: PyReadonlyArray1<'py, f32>,
    ) -> PyResult<()> {
        let id = ConceptId::from_string(concept_id);
        let vec = vector.as_slice()?.to_vec();
        
        self.vectors.add_vector(id, vec)
            .map_err(|e| StorageError(format!("Failed to add vector: {}", e)))?;
        
        Ok(())
    }
    
    /// Get vector for a concept
    fn get_vector<'py>(&self, concept_id: &str, py: Python<'py>) -> PyResult<Option<&'py PyArray1<f32>>> {
        let id = ConceptId::from_string(concept_id);
        
        if let Some(vec) = self.vectors.get_vector(&id)
            .map_err(|e| StorageError(format!("Failed to get vector: {}", e)))? {
            Ok(Some(PyArray1::from_vec(py, vec)))
        } else {
            Ok(None)
        }
    }
    
    /// Compute exact distance between two concept vectors
    fn distance(&self, concept_id1: &str, concept_id2: &str) -> PyResult<f32> {
        let id1 = ConceptId::from_string(concept_id1);
        let id2 = ConceptId::from_string(concept_id2);
        
        self.vectors.distance(&id1, &id2)
            .map_err(|e| StorageError(format!("Failed to compute distance: {}", e)).into())
    }
    
    /// Compute approximate distance (using quantization)
    fn approximate_distance(&self, concept_id1: &str, concept_id2: &str) -> PyResult<f32> {
        let id1 = ConceptId::from_string(concept_id1);
        let id2 = ConceptId::from_string(concept_id2);
        
        self.vectors.approximate_distance(&id1, &id2)
            .map_err(|e| StorageError(format!("Failed to compute approximate distance: {}", e)).into())
    }
    
    /// Train vector quantizer on current vectors
    fn train_quantizer(&self) -> PyResult<()> {
        // Get all vectors
        let vectors: Vec<Vec<f32>> = vec![];  // TODO: collect from vector store
        
        self.vectors.train_quantizer(vectors)
            .map_err(|e| StorageError(format!("Failed to train quantizer: {}", e)))?;
        
        Ok(())
    }
    
    // -------------------------------------------------------------------------
    // Search Operations
    // -------------------------------------------------------------------------
    
    /// Search concepts by text content
    fn search_text(&self, query: &str, py: Python) -> PyResult<PyObject> {
        let results: Vec<String> = self.index.search_text(query)
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, results).into())
    }
    
    /// Get concepts in a time range
    fn get_concepts_in_range(&self, start: u64, end: u64, py: Python) -> PyResult<PyObject> {
        let results: Vec<String> = self.index.get_concepts_in_time_range(start, end)
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, results).into())
    }
    
    // -------------------------------------------------------------------------
    // Transaction Operations
    // -------------------------------------------------------------------------
    
    /// Begin a new transaction
    fn begin_transaction(&self) -> PyResult<u64> {
        self.wal.begin_transaction()
            .map_err(|e| StorageError(format!("Failed to begin transaction: {}", e)).into())
    }
    
    /// Commit a transaction
    fn commit_transaction(&self, transaction_id: u64) -> PyResult<()> {
        self.wal.commit(transaction_id)
            .map_err(|e| StorageError(format!("Failed to commit transaction: {}", e)).into())
    }
    
    /// Rollback a transaction
    fn rollback_transaction(&self, transaction_id: u64) -> PyResult<()> {
        self.wal.rollback(transaction_id)
            .map_err(|e| StorageError(format!("Failed to rollback transaction: {}", e)).into())
    }
    
    /// Create a transaction context manager
    fn transaction(slf: Py<Self>) -> PyResult<PyTransaction> {
        Ok(PyTransaction {
            transaction_id: None,
            committed: false,
            store: slf,
        })
    }
    
    // -------------------------------------------------------------------------
    // Maintenance Operations
    // -------------------------------------------------------------------------
    
    /// Checkpoint WAL (truncate after persisting)
    fn checkpoint(&self) -> PyResult<()> {
        self.wal.checkpoint()
            .map_err(|e| StorageError(format!("Failed to checkpoint: {}", e)).into())
    }
    
    /// Trigger LSM compaction
    fn compact(&self) -> PyResult<()> {
        // TODO: Trigger compaction
        Ok(())
    }
    
    /// Save all data to disk
    fn save(&self) -> PyResult<()> {
        self.vectors.save()
            .map_err(|e| StorageError(format!("Failed to save vectors: {}", e)))?;
        
        Ok(())
    }
    
    /// Get storage statistics
    fn stats(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        
        // Vector stats
        let vec_stats = self.vectors.stats();
        dict.set_item("vector_count", vec_stats.vector_count)?;
        dict.set_item("compressed_count", vec_stats.compressed_count)?;
        dict.set_item("total_size_bytes", vec_stats.total_size_bytes)?;
        dict.set_item("compression_ratio", vec_stats.compression_ratio)?;
        
        // Index stats
        dict.set_item("concept_count", self.index.get_all_concept_ids().len())?;
        
        Ok(dict.into())
    }
    
    // -------------------------------------------------------------------------
    // Context Manager Support
    // -------------------------------------------------------------------------
    
    fn __enter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }
    
    fn __exit__(
        &self,
        _exc_type: PyObject,
        _exc_value: PyObject,
        _traceback: PyObject,
    ) -> PyResult<bool> {
        // Save on exit
        self.save()?;
        Ok(false)
    }
}

// =============================================================================
// Module Definition
// =============================================================================

/// Python module for Sutra storage engine
#[pymodule]
fn sutra_storage(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyGraphStore>()?;
    m.add_class::<PyConceptId>()?;
    m.add_class::<PyConcept>()?;
    m.add_class::<PyAssociation>()?;
    m.add_class::<PyTransaction>()?;
    
    // Add module version
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    
    Ok(())
}
