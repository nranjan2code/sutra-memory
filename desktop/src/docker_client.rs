//! Docker-based storage client for Desktop Edition
//!
//! This module provides a thin client that connects to local Docker services.
//! Much simpler than embedding everything - just talks to localhost Docker.

use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Docker storage client - connects to local Docker storage server
pub struct DockerStorageClient {
    base_url: String,
    client: reqwest::Client,
}

#[derive(Serialize)]
struct LearnRequest {
    content: String,
}

#[derive(Deserialize)]
struct LearnResponse {
    concept_id: String,
    message: String,
}

#[derive(Serialize)]
struct QueryRequest {
    query: String,
    max_results: Option<usize>,
}

#[derive(Deserialize)]
pub struct QueryResponse {
    pub concepts: Vec<ConceptResult>,
    pub took_ms: u64,
}

#[derive(Deserialize)]
pub struct ConceptResult {
    pub concept_id: String,
    pub content: String,
    pub confidence: f32,
}

impl DockerStorageClient {
    /// Create a new Docker client connecting to localhost API
    pub fn new(port: u16) -> Self {
        let base_url = format!("http://127.0.0.1:{}", port);
        let client = reqwest::Client::builder()
            .timeout(Duration::from_secs(30))
            .build()
            .expect("Failed to create HTTP client");

        Self { base_url, client }
    }

    /// Check if Docker services are running
    pub async fn health_check(&self) -> Result<bool> {
        let url = format!("{}/health", self.base_url);
        match self.client.get(&url).send().await {
            Ok(resp) => Ok(resp.status().is_success()),
            Err(_) => Ok(false),
        }
    }

    /// Learn a new concept via Docker API
    pub async fn learn(&self, content: String) -> Result<String> {
        let url = format!("{}/api/v1/learn", self.base_url);
        let request = LearnRequest { content };

        let response = self
            .client
            .post(&url)
            .json(&request)
            .send()
            .await
            .context("Failed to send learn request")?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            anyhow::bail!("Learn failed ({}): {}", status, error_text);
        }

        let learn_resp: LearnResponse = response
            .json()
            .await
            .context("Failed to parse learn response")?;

        Ok(learn_resp.concept_id)
    }

    /// Query concepts via Docker API
    pub async fn query(&self, query: String, max_results: Option<usize>) -> Result<QueryResponse> {
        let url = format!("{}/api/v1/reason", self.base_url);
        let request = QueryRequest { query, max_results };

        let response = self
            .client
            .post(&url)
            .json(&request)
            .send()
            .await
            .context("Failed to send query request")?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            anyhow::bail!("Query failed ({}): {}", status, error_text);
        }

        let query_resp: QueryResponse = response
            .json()
            .await
            .context("Failed to parse query response")?;

        Ok(query_resp)
    }

    /// Get all concepts (for knowledge browser)
    pub async fn list_concepts(&self) -> Result<Vec<ConceptResult>> {
        let url = format!("{}/api/v1/concepts", self.base_url);

        let response = self
            .client
            .get(&url)
            .send()
            .await
            .context("Failed to list concepts")?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            anyhow::bail!("List concepts failed ({}): {}", status, error_text);
        }

        let concepts: Vec<ConceptResult> = response
            .json()
            .await
            .context("Failed to parse concepts")?;

        Ok(concepts)
    }

    /// Delete a concept by ID
    pub async fn delete_concept(&self, concept_id: &str) -> Result<()> {
        let url = format!("{}/api/v1/concepts/{}", self.base_url, concept_id);

        let response = self
            .client
            .delete(&url)
            .send()
            .await
            .context("Failed to delete concept")?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            anyhow::bail!("Delete failed ({}): {}", status, error_text);
        }

        Ok(())
    }

    /// Get storage statistics
    pub async fn get_stats(&self) -> Result<StorageStats> {
        let url = format!("{}/api/v1/stats", self.base_url);

        let response = self
            .client
            .get(&url)
            .send()
            .await
            .context("Failed to get stats")?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await.unwrap_or_default();
            anyhow::bail!("Stats failed ({}): {}", status, error_text);
        }

        let stats: StorageStats = response
            .json()
            .await
            .context("Failed to parse stats")?;

        Ok(stats)
    }
}

#[derive(Deserialize)]
pub struct StorageStats {
    pub total_concepts: usize,
    pub total_edges: usize,
    pub avg_query_time_ms: f64,
}

/// Helper to check if Docker is running and services are up
pub async fn check_docker_services() -> Result<bool> {
    let client = DockerStorageClient::new(8080);
    client.health_check().await
}

/// Helper to get human-readable error messages
pub fn docker_error_message() -> String {
    r#"Docker services not running!

To start Sutra Desktop services:
1. Open Terminal
2. Run: cd /path/to/sutra-memory
3. Run: ./sutra desktop start

This will start:
- Storage Server (localhost:50051)
- Embedding Service (Docker internal)
- API Server (localhost:8080)

First time? It may take 2-3 minutes to download images (~500MB).
"#
    .to_string()
}
