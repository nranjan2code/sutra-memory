/// Binary Distribution Server
/// 
/// Serves storage-server binaries to agents with version management and checksum verification.
/// This enables zero-touch deployment where agents can automatically download the correct binary.

use axum::{
    Router,
    extract::{Path, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use std::collections::HashMap;
use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::RwLock;
use tower_http::services::ServeDir;

/// Binary metadata including version and checksum
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinaryInfo {
    pub version: String,
    pub platform: String,
    pub arch: String,
    pub checksum: String,
    pub size_bytes: u64,
    pub path: String,
    pub uploaded_at: u64,
}

/// Binary distribution service state
#[derive(Clone)]
pub struct BinaryDistribution {
    binaries_dir: PathBuf,
    registry: Arc<RwLock<HashMap<String, BinaryInfo>>>,
}

impl BinaryDistribution {
    pub fn new(binaries_dir: PathBuf) -> Self {
        std::fs::create_dir_all(&binaries_dir).ok();
        
        Self {
            binaries_dir,
            registry: Arc::new(RwLock::new(HashMap::new())),
        }
    }
    
    /// Register a binary in the distribution system
    pub async fn register_binary(
        &self,
        version: String,
        platform: String,
        arch: String,
        binary_path: PathBuf,
    ) -> anyhow::Result<BinaryInfo> {
        log::info!("📦 Registering binary: {} {} {}", version, platform, arch);
        
        // Calculate checksum
        let checksum = calculate_checksum(&binary_path).await?;
        
        // Get file size
        let metadata = tokio::fs::metadata(&binary_path).await?;
        let size_bytes = metadata.len();
        
        // Copy binary to distribution directory
        let filename = format!("storage-server-{}-{}-{}", version, platform, arch);
        let dest_path = self.binaries_dir.join(&filename);
        tokio::fs::copy(&binary_path, &dest_path).await?;
        
        let binary_info = BinaryInfo {
            version: version.clone(),
            platform: platform.clone(),
            arch: arch.clone(),
            checksum,
            size_bytes,
            path: filename.clone(),
            uploaded_at: current_timestamp(),
        };
        
        // Store in registry
        let key = format!("{}-{}-{}", version, platform, arch);
        self.registry.write().await.insert(key, binary_info.clone());
        
        log::info!("✅ Binary registered: {} ({})", filename, format_size(size_bytes));
        
        Ok(binary_info)
    }
    
    /// Get binary info for specific version/platform/arch
    pub async fn get_binary_info(
        &self,
        version: &str,
        platform: &str,
        arch: &str,
    ) -> Option<BinaryInfo> {
        let key = format!("{}-{}-{}", version, platform, arch);
        self.registry.read().await.get(&key).cloned()
    }
    
    /// List all available binaries
    pub async fn list_binaries(&self) -> Vec<BinaryInfo> {
        self.registry.read().await.values().cloned().collect()
    }
    
    /// Get latest version for a platform/arch
    pub async fn get_latest_version(&self, platform: &str, arch: &str) -> Option<BinaryInfo> {
        let registry = self.registry.read().await;
        
        registry.values()
            .filter(|b| b.platform == platform && b.arch == arch)
            .max_by_key(|b| b.uploaded_at)
            .cloned()
    }
}

/// Calculate SHA256 checksum of a file
async fn calculate_checksum(path: &PathBuf) -> anyhow::Result<String> {
    let bytes = tokio::fs::read(path).await?;
    let mut hasher = Sha256::new();
    hasher.update(&bytes);
    let result = hasher.finalize();
    Ok(hex::encode(result))
}

/// Format byte size for human-readable display
fn format_size(bytes: u64) -> String {
    const UNITS: &[&str] = &["B", "KB", "MB", "GB"];
    let mut size = bytes as f64;
    let mut unit_idx = 0;
    
    while size >= 1024.0 && unit_idx < UNITS.len() - 1 {
        size /= 1024.0;
        unit_idx += 1;
    }
    
    format!("{:.2} {}", size, UNITS[unit_idx])
}

fn current_timestamp() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

// ===== HTTP API Handlers =====

/// List all available binaries
async fn list_binaries_handler(
    State(distribution): State<BinaryDistribution>,
) -> Json<Vec<BinaryInfo>> {
    Json(distribution.list_binaries().await)
}

/// Get specific binary info
async fn get_binary_info_handler(
    State(distribution): State<BinaryDistribution>,
    Path((version, platform, arch)): Path<(String, String, String)>,
) -> Result<Json<BinaryInfo>, StatusCode> {
    match distribution.get_binary_info(&version, &platform, &arch).await {
        Some(info) => Ok(Json(info)),
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// Get latest binary info for platform/arch
async fn get_latest_binary_handler(
    State(distribution): State<BinaryDistribution>,
    Path((platform, arch)): Path<(String, String)>,
) -> Result<Json<BinaryInfo>, StatusCode> {
    match distribution.get_latest_version(&platform, &arch).await {
        Some(info) => Ok(Json(info)),
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// Verify binary checksum
#[derive(Deserialize)]
struct VerifyRequest {
    checksum: String,
}

#[derive(Serialize)]
struct VerifyResponse {
    valid: bool,
    expected_checksum: String,
}

async fn verify_checksum_handler(
    State(distribution): State<BinaryDistribution>,
    Path((version, platform, arch)): Path<(String, String, String)>,
    Json(request): Json<VerifyRequest>,
) -> Result<Json<VerifyResponse>, StatusCode> {
    match distribution.get_binary_info(&version, &platform, &arch).await {
        Some(info) => Ok(Json(VerifyResponse {
            valid: info.checksum == request.checksum,
            expected_checksum: info.checksum,
        })),
        None => Err(StatusCode::NOT_FOUND),
    }
}

/// Create HTTP router for binary distribution
pub fn create_router(distribution: BinaryDistribution, binaries_dir: PathBuf) -> Router {
    Router::new()
        // Metadata endpoints
        .route("/api/binaries", axum::routing::get(list_binaries_handler))
        .route("/api/binaries/:version/:platform/:arch", 
               axum::routing::get(get_binary_info_handler))
        .route("/api/binaries/latest/:platform/:arch", 
               axum::routing::get(get_latest_binary_handler))
        .route("/api/binaries/:version/:platform/:arch/verify", 
               axum::routing::post(verify_checksum_handler))
        // File serving - actual binary downloads
        .nest_service("/binaries", ServeDir::new(binaries_dir))
        .with_state(distribution)
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_checksum_calculation() {
        // Create a temporary file
        let temp_dir = std::env::temp_dir();
        let test_file = temp_dir.join("test_binary");
        tokio::fs::write(&test_file, b"test content").await.unwrap();
        
        let checksum = calculate_checksum(&test_file).await.unwrap();
        
        // SHA256 of "test content"
        assert_eq!(checksum.len(), 64); // SHA256 produces 64 hex characters
        
        tokio::fs::remove_file(test_file).await.ok();
    }
    
    #[test]
    fn test_format_size() {
        assert_eq!(format_size(1024), "1.00 KB");
        assert_eq!(format_size(1024 * 1024), "1.00 MB");
        assert_eq!(format_size(1024 * 1024 * 1024), "1.00 GB");
    }
}
