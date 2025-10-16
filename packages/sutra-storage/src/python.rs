/// Simplified Python bindings for Sutra Storage Engine
/// 
/// This is a minimal working version to establish the Python interface.
/// Full integration will be completed incrementally.

use pyo3::prelude::*;
use pyo3::exceptions::PyException;
use pyo3::types::{PyDict, PyList};
use numpy::{PyArray1, PyReadonlyArray1};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

use crate::types::ConceptId;
use crate::vectors::{VectorStore, VectorConfig};
use crate::index::GraphIndex;

// =============================================================================
// Error Handling
// =============================================================================

#[derive(Debug)]
struct StorageError(String);

impl From<StorageError> for PyErr {
    fn from(err: StorageError) -> PyErr {
        PyException::new_err(format!("Storage error: {}", err.0))
    }
}

impl From<std::io::Error> for StorageError {
    fn from(err: std::io::Error) -> StorageError {
        StorageError(format!("IO error: {}", err))
    }
}

impl From<anyhow::Error> for StorageError {
    fn from(err: anyhow::Error) -> StorageError {
        StorageError(format!("{}", err))
    }
}

// =============================================================================
// Python GraphStore
// =============================================================================

/// High-level Python interface to the storage engine
#[pyclass(name = "GraphStore")]
struct PyGraphStore {
    vectors: Arc<Mutex<VectorStore>>,
    index: Arc<Mutex<GraphIndex>>,
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
        
        // Create directory
        std::fs::create_dir_all(&path_buf)
            .map_err(|e| StorageError(format!("Failed to create directory: {}", e)))?;
        
        // Initialize vector store - load if exists, create if new
        let vectors_path = path_buf.join("vectors");
        let vectors = Arc::new(Mutex::new(
            if vectors_path.join("config.json").exists() {
                // Load existing vector store
                VectorStore::load(&vectors_path)
                    .map_err(|e| StorageError(format!("Failed to load vector store: {}", e)))?
            } else {
                // Create new vector store
                let vector_config = VectorConfig {
                    dimension: vector_dimension,
                    use_compression,
                    num_subvectors: vector_dimension / 8,
                    num_centroids: 256,
                };
                VectorStore::new(&vectors_path, vector_config)
                    .map_err(|e| StorageError(format!("Failed to create vector store: {}", e)))?
            }
        ));        // Initialize index
        let index = Arc::new(Mutex::new(GraphIndex::new()));
        
        Ok(Self {
            vectors,
            index,
            path: path_buf,
        })
    }
    
    // -------------------------------------------------------------------------
    // Vector Operations
    // -------------------------------------------------------------------------
    
    /// Add a vector for a concept
    fn add_vector(
        &self,
        concept_id: &str,
        vector: PyReadonlyArray1<f32>,
    ) -> PyResult<()> {
        let id = ConceptId::from_string(concept_id);
        let vec = vector.as_slice()?.to_vec();
        
        let vectors = self.vectors.lock().unwrap();
        vectors.add_vector(id, vec)
            .map_err(|e| StorageError(format!("Failed to add vector: {}", e)))?;
        
        Ok(())
    }
    
    /// Get vector for a concept
    fn get_vector<'py>(
        &self,
        concept_id: &str,
        py: Python<'py>,
    ) -> PyResult<Option<&'py PyArray1<f32>>> {
        let id = ConceptId::from_string(concept_id);
        
        let vectors = self.vectors.lock().unwrap();
        match vectors.get_vector(id) {
            Some(vec) => Ok(Some(PyArray1::from_vec(py, vec))),
            None => Ok(None),
        }
    }
    
    /// Remove a vector
    fn remove_vector(&self, concept_id: &str) -> PyResult<()> {
        let id = ConceptId::from_string(concept_id);
        
        let vectors = self.vectors.lock().unwrap();
        vectors.remove_vector(id)
            .map_err(|e| StorageError(format!("Failed to remove vector: {}", e)))?;
        
        Ok(())
    }
    
    /// Compute exact distance between two vectors
    fn distance(&self, concept_id1: &str, concept_id2: &str) -> PyResult<f32> {
        let id1 = ConceptId::from_string(concept_id1);
        let id2 = ConceptId::from_string(concept_id2);
        
        let vectors = self.vectors.lock().unwrap();
        vectors.distance(id1, id2)
            .map_err(|e| StorageError(format!("Failed to compute distance: {}", e)).into())
    }
    
    /// Compute approximate distance (using quantization)
    fn approximate_distance(&self, concept_id1: &str, concept_id2: &str) -> PyResult<f32> {
        let id1 = ConceptId::from_string(concept_id1);
        let id2 = ConceptId::from_string(concept_id2);
        
        let vectors = self.vectors.lock().unwrap();
        vectors.approximate_distance(id1, id2)
            .map_err(|e| StorageError(format!("Failed to compute approximate distance: {}", e)).into())
    }
    
    /// Train vector quantizer
    fn train_quantizer(&self, training_vectors: Vec<PyReadonlyArray1<f32>>) -> PyResult<()> {
        let vectors_data: Result<Vec<Vec<f32>>, _> = training_vectors
            .iter()
            .map(|arr| arr.as_slice().map(|s| s.to_vec()))
            .collect();
        
        let vectors_data = vectors_data?;
        
        let vectors = self.vectors.lock().unwrap();
        vectors.train_quantizer(Some(vectors_data))
            .map_err(|e| StorageError(format!("Failed to train quantizer: {}", e)))?;
        
        Ok(())
    }
    
    // -------------------------------------------------------------------------
    // Index Operations
    // -------------------------------------------------------------------------
    
    /// Add association between concepts
    fn add_association(&self, source_id: &str, target_id: &str) -> PyResult<()> {
        let source = ConceptId::from_string(source_id);
        let target = ConceptId::from_string(target_id);
        
        let index = self.index.lock().unwrap();
        index.add_edge(source, target);
        
        Ok(())
    }
    
    /// Get neighbors of a concept
    fn get_neighbors(&self, concept_id: &str, py: Python) -> PyResult<PyObject> {
        let id = ConceptId::from_string(concept_id);
        
        let index = self.index.lock().unwrap();
        let neighbors: Vec<String> = index.get_neighbors(id)
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, neighbors).into())
    }
    
    /// Search by text
    fn search_text(&self, query: &str, py: Python) -> PyResult<PyObject> {
        let words: Vec<String> = query.split_whitespace().map(|s| s.to_lowercase()).collect();
        
        let index = self.index.lock().unwrap();
        let results: Vec<String> = index.search_by_words(&words)
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, results).into())
    }
    
    /// Get concepts in time range
    fn get_concepts_in_range(&self, start: u64, end: u64, py: Python) -> PyResult<PyObject> {
        let index = self.index.lock().unwrap();
        let results: Vec<String> = index.query_time_range(start, end)
            .into_iter()
            .map(|id| id.to_hex())
            .collect();
        
        Ok(PyList::new(py, results).into())
    }
    
    // -------------------------------------------------------------------------
    // Maintenance
    // -------------------------------------------------------------------------
    
    /// Save all data to disk
    fn save(&self) -> PyResult<()> {
        let vectors = self.vectors.lock().unwrap();
        vectors.save()
            .map_err(|e| StorageError(format!("Failed to save: {}", e)))?;
        
        Ok(())
    }
    
    /// Get storage statistics
    fn stats(&self, py: Python) -> PyResult<PyObject> {
        let dict = PyDict::new(py);
        
        let vectors = self.vectors.lock().unwrap();
        let vec_stats = vectors.stats();
        
        dict.set_item("total_vectors", vec_stats.total_vectors)?;
        dict.set_item("compressed_vectors", vec_stats.compressed_vectors)?;
        dict.set_item("dimension", vec_stats.dimension)?;
        dict.set_item("raw_size_bytes", vec_stats.raw_size_bytes)?;
        dict.set_item("compressed_size_bytes", vec_stats.compressed_size_bytes)?;
        dict.set_item("compression_ratio", vec_stats.compression_ratio)?;
        dict.set_item("quantizer_trained", vec_stats.quantizer_trained)?;
        
        let index = self.index.lock().unwrap();
        let index_stats = index.stats();
        dict.set_item("total_concepts", index_stats.total_concepts)?;
        dict.set_item("total_edges", index_stats.total_edges)?;
        dict.set_item("total_words", index_stats.total_words)?;
        
        Ok(dict.into())
    }
    
    // -------------------------------------------------------------------------
    // Context Manager
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
        self.save()?;
        Ok(false)
    }
}

// =============================================================================
// Module Definition
// =============================================================================

#[pymodule]
fn sutra_storage(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyGraphStore>()?;
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    Ok(())
}
