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

    // ========================================================================
    // DesktopError Display Tests
    // ========================================================================

    #[test]
    fn test_storage_init_error_display() {
        let err = DesktopError::StorageInit("disk full".to_string());
        assert!(err.to_string().contains("Failed to initialize storage"));
        assert!(err.to_string().contains("disk full"));
    }

    #[test]
    fn test_embedding_init_error_display() {
        let err = DesktopError::EmbeddingInit("network timeout".to_string());
        assert!(err.to_string().contains("embedding provider"));
        assert!(err.to_string().contains("network timeout"));
    }

    #[test]
    fn test_nlg_init_error_display() {
        let err = DesktopError::NlgInit("model load failed".to_string());
        assert!(err.to_string().contains("NLG provider"));
        assert!(err.to_string().contains("model load failed"));
    }

    #[test]
    fn test_data_directory_error_display() {
        let err = DesktopError::DataDirectory("permission denied".to_string());
        assert!(err.to_string().contains("data directory"));
        assert!(err.to_string().contains("permission denied"));
    }

    #[test]
    fn test_settings_error_display() {
        let err = DesktopError::Settings("corrupted file".to_string());
        assert!(err.to_string().contains("Settings error"));
        assert!(err.to_string().contains("corrupted file"));
    }

    #[test]
    fn test_learning_error_display() {
        let err = DesktopError::Learning("invalid content".to_string());
        assert!(err.to_string().contains("Learning failed"));
        assert!(err.to_string().contains("invalid content"));
    }

    #[test]
    fn test_query_error_display() {
        let err = DesktopError::Query("syntax error".to_string());
        assert!(err.to_string().contains("Query failed"));
        assert!(err.to_string().contains("syntax error"));
    }

    #[test]
    fn test_serialization_error_display() {
        let err = DesktopError::Serialization("invalid JSON".to_string());
        assert!(err.to_string().contains("Serialization error"));
        assert!(err.to_string().contains("invalid JSON"));
    }

    #[test]
    fn test_runtime_error_display() {
        let err = DesktopError::Runtime("thread panic".to_string());
        assert!(err.to_string().contains("Runtime error"));
        assert!(err.to_string().contains("thread panic"));
    }

    #[test]
    fn test_invalid_config_error_display() {
        let err = DesktopError::InvalidConfig("bad value".to_string());
        assert!(err.to_string().contains("Invalid configuration"));
        assert!(err.to_string().contains("bad value"));
    }

    // ========================================================================
    // UserError Tests
    // ========================================================================

    #[test]
    fn test_embedding_init_user_error() {
        let err = DesktopError::EmbeddingInit("test error".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "Embedding Model Download Failed");
        assert!(user_err.recoverable);
        assert!(!user_err.actions.is_empty());
        assert!(user_err.message.contains("test error"));
        assert!(user_err.message.contains("text-only mode"));
    }

    #[test]
    fn test_nlg_init_user_error() {
        let err = DesktopError::NlgInit("model missing".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "NLG Model Unavailable");
        assert!(user_err.recoverable);
        assert!(user_err.message.contains("model missing"));
        assert!(user_err.message.contains("without NLG"));
    }

    #[test]
    fn test_storage_init_user_error() {
        let err = DesktopError::StorageInit("disk error".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "Storage Initialization Failed");
        assert!(!user_err.recoverable); // Critical error
        assert!(user_err.message.contains("disk error"));
        assert!(user_err.message.contains("critical error"));
    }

    #[test]
    fn test_data_directory_user_error() {
        let err = DesktopError::DataDirectory("no permission".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "Data Directory Error");
        assert!(user_err.recoverable);
        assert!(user_err.message.contains("no permission"));
    }

    #[test]
    fn test_settings_user_error() {
        let err = DesktopError::Settings("parse failed".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "Settings Error");
        assert!(user_err.recoverable);
        assert!(user_err.message.contains("Default settings will be used"));
    }

    #[test]
    fn test_learning_user_error() {
        let err = DesktopError::Learning("content too large".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "Learning Failed");
        assert!(user_err.recoverable);
        assert!(user_err.message.contains("content too large"));
    }

    #[test]
    fn test_query_user_error() {
        let err = DesktopError::Query("invalid syntax".to_string());
        let user_err = UserError::from_desktop_error(&err);

        assert_eq!(user_err.title, "Query Failed");
        assert!(user_err.recoverable);
        assert!(user_err.message.contains("invalid syntax"));
    }

    #[test]
    fn test_user_error_actions_not_empty() {
        let errors = vec![
            DesktopError::EmbeddingInit("test".into()),
            DesktopError::NlgInit("test".into()),
            DesktopError::StorageInit("test".into()),
            DesktopError::DataDirectory("test".into()),
            DesktopError::Settings("test".into()),
        ];

        for err in errors {
            let user_err = UserError::from_desktop_error(&err);
            assert!(!user_err.actions.is_empty(), "Error type should have actions: {:?}", err);
        }
    }

    // ========================================================================
    // Error Conversion Tests
    // ========================================================================

    #[test]
    fn test_io_error_conversion() {
        let io_err = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let desktop_err: DesktopError = io_err.into();

        match desktop_err {
            DesktopError::Io(_) => (),
            _ => panic!("Expected Io variant"),
        }
    }

    #[test]
    fn test_serde_json_error_conversion() {
        let json_str = "{invalid json}";
        let result: std::result::Result<serde_json::Value, serde_json::Error> = serde_json::from_str(json_str);
        let json_err = result.unwrap_err();

        let desktop_err: DesktopError = json_err.into();

        match desktop_err {
            DesktopError::Serialization(msg) => {
                assert!(!msg.is_empty());
            }
            _ => panic!("Expected Serialization variant"),
        }
    }

    // ========================================================================
    // Error Trait Implementation Tests
    // ========================================================================

    #[test]
    fn test_error_trait_implemented() {
        let err = DesktopError::StorageInit("test".to_string());
        let _err_ref: &dyn std::error::Error = &err;
    }

    #[test]
    fn test_error_source() {
        use std::error::Error;
        let io_err = std::io::Error::new(std::io::ErrorKind::NotFound, "file not found");
        let desktop_err: DesktopError = io_err.into();

        assert!(desktop_err.source().is_none()); // DesktopError doesn't expose source currently
    }

    // ========================================================================
    // Edge Cases
    // ========================================================================

    #[test]
    fn test_empty_error_message() {
        let err = DesktopError::StorageInit("".to_string());
        let display = err.to_string();
        assert!(display.contains("Failed to initialize storage"));
    }

    #[test]
    fn test_very_long_error_message() {
        let long_msg = "x".repeat(10000);
        let err = DesktopError::Learning(long_msg.clone());
        let display = err.to_string();
        assert!(display.contains(&long_msg));
    }

    #[test]
    fn test_error_with_special_characters() {
        let msg = "Error: \n\t\r special \"chars\" and 'quotes'";
        let err = DesktopError::Query(msg.to_string());
        let display = err.to_string();
        assert!(display.contains(msg));
    }
}
