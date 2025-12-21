//! Error types for Sutra Desktop Edition
//!
//! Comprehensive error handling to eliminate unwrap/panic points.
//! Provides user-friendly error messages and recovery strategies.

use std::fmt;

/// Result type for desktop operations
pub type Result<T> = std::result::Result<T, DesktopError>;

/// Desktop application errors
#[derive(Debug)]
pub enum DesktopError {
    /// Storage initialization failed
    StorageInit(String),

    /// Embedding provider initialization failed
    EmbeddingInit(String),

    /// NLG provider initialization failed
    NlgInit(String),

    /// Data directory creation failed
    DataDirectory(String),

    /// Settings load/save failed
    Settings(String),

    /// Learning operation failed
    Learning(String),

    /// Query operation failed
    Query(String),

    /// File I/O error
    Io(std::io::Error),

    /// Serialization error
    Serialization(String),

    /// Runtime error
    Runtime(String),

    /// Invalid configuration
    InvalidConfig(String),
}

impl fmt::Display for DesktopError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            DesktopError::StorageInit(msg) => {
                write!(f, "Failed to initialize storage: {}", msg)
            }
            DesktopError::EmbeddingInit(msg) => {
                write!(f, "Failed to initialize embedding provider: {}", msg)
            }
            DesktopError::NlgInit(msg) => {
                write!(f, "Failed to initialize NLG provider: {}", msg)
            }
            DesktopError::DataDirectory(msg) => {
                write!(f, "Failed to create data directory: {}", msg)
            }
            DesktopError::Settings(msg) => {
                write!(f, "Settings error: {}", msg)
            }
            DesktopError::Learning(msg) => {
                write!(f, "Learning failed: {}", msg)
            }
            DesktopError::Query(msg) => {
                write!(f, "Query failed: {}", msg)
            }
            DesktopError::Io(err) => {
                write!(f, "I/O error: {}", err)
            }
            DesktopError::Serialization(msg) => {
                write!(f, "Serialization error: {}", msg)
            }
            DesktopError::Runtime(msg) => {
                write!(f, "Runtime error: {}", msg)
            }
            DesktopError::InvalidConfig(msg) => {
                write!(f, "Invalid configuration: {}", msg)
            }
        }
    }
}

impl std::error::Error for DesktopError {}

impl From<std::io::Error> for DesktopError {
    fn from(err: std::io::Error) -> Self {
        DesktopError::Io(err)
    }
}

impl From<serde_json::Error> for DesktopError {
    fn from(err: serde_json::Error) -> Self {
        DesktopError::Serialization(err.to_string())
    }
}

/// User-facing error information
///
/// Provides actionable information for displaying errors to users.
pub struct UserError {
    /// Error title (short description)
    pub title: String,

    /// Detailed error message
    pub message: String,

    /// Suggested actions for recovery
    pub actions: Vec<String>,

    /// Whether this error is recoverable
    pub recoverable: bool,
}

impl UserError {
    /// Convert DesktopError to user-friendly error
    pub fn from_desktop_error(err: &DesktopError) -> Self {
        match err {
            DesktopError::EmbeddingInit(msg) => UserError {
                title: "Embedding Model Download Failed".to_string(),
                message: format!(
                    "Could not download or initialize the embedding model.\n\n\
                     Error: {}\n\n\
                     The app can continue in text-only mode, but semantic search \
                     will be unavailable.",
                    msg
                ),
                actions: vec![
                    "Retry Download".to_string(),
                    "Continue in Text-Only Mode".to_string(),
                    "Check Network Connection".to_string(),
                    "View Help".to_string(),
                ],
                recoverable: true,
            },

            DesktopError::NlgInit(msg) => UserError {
                title: "NLG Model Unavailable".to_string(),
                message: format!(
                    "Could not initialize the natural language generation model.\n\n\
                     Error: {}\n\n\
                     The app will continue without NLG features.",
                    msg
                ),
                actions: vec![
                    "Continue Without NLG".to_string(),
                    "Retry".to_string(),
                ],
                recoverable: true,
            },

            DesktopError::StorageInit(msg) => UserError {
                title: "Storage Initialization Failed".to_string(),
                message: format!(
                    "Could not initialize the storage engine.\n\n\
                     Error: {}\n\n\
                     This is a critical error. Please check disk space and permissions.",
                    msg
                ),
                actions: vec![
                    "Change Data Directory".to_string(),
                    "Check Disk Space".to_string(),
                    "Exit".to_string(),
                ],
                recoverable: false,
            },

            DesktopError::DataDirectory(msg) => UserError {
                title: "Data Directory Error".to_string(),
                message: format!(
                    "Could not create or access the data directory.\n\n\
                     Error: {}\n\n\
                     Please ensure you have write permissions.",
                    msg
                ),
                actions: vec![
                    "Choose Different Directory".to_string(),
                    "Check Permissions".to_string(),
                ],
                recoverable: true,
            },

            DesktopError::Settings(msg) => UserError {
                title: "Settings Error".to_string(),
                message: format!(
                    "Could not load or save settings.\n\n\
                     Error: {}\n\n\
                     Default settings will be used.",
                    msg
                ),
                actions: vec![
                    "Continue with Defaults".to_string(),
                    "Reset Settings".to_string(),
                ],
                recoverable: true,
            },

            DesktopError::Learning(msg) => UserError {
                title: "Learning Failed".to_string(),
                message: format!(
                    "Could not learn the provided content.\n\n\
                     Error: {}",
                    msg
                ),
                actions: vec![
                    "Try Again".to_string(),
                    "Simplify Content".to_string(),
                ],
                recoverable: true,
            },

            DesktopError::Query(msg) => UserError {
                title: "Query Failed".to_string(),
                message: format!(
                    "Could not process your query.\n\n\
                     Error: {}",
                    msg
                ),
                actions: vec![
                    "Try Again".to_string(),
                    "Rephrase Query".to_string(),
                ],
                recoverable: true,
            },

            _ => UserError {
                title: "Error".to_string(),
                message: format!("{}", err),
                actions: vec!["OK".to_string()],
                recoverable: true,
            },
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_error_display() {
        let err = DesktopError::EmbeddingInit("network timeout".to_string());
        assert!(err.to_string().contains("embedding provider"));
    }

    #[test]
    fn test_user_error_creation() {
        let err = DesktopError::EmbeddingInit("test error".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert!(user_err.recoverable);
        assert!(!user_err.actions.is_empty());
        assert!(user_err.message.contains("test error"));
    }

    #[test]
    fn test_io_error_conversion() {
        let io_err = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let desktop_err: DesktopError = io_err.into();

        match desktop_err {
            DesktopError::Io(_) => (),
            _ => panic!("Expected Io variant"),
        }
    }
}
