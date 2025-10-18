use std::collections::HashMap;
use std::sync::Arc;
use std::path::PathBuf;
use tokio::sync::RwLock;
use tonic::{transport::Server, Request, Response, Status};
use chrono::{DateTime, TimeZone, Utc};
use sutra_grid_events::{EventEmitter, GridEvent};

// Include generated protobuf code
pub mod grid {
    tonic::include_proto!("grid");
}

pub mod agent {
    tonic::include_proto!("agent");
}

mod binary_server;

// ===== Data Structures =====

#[derive(Debug, Clone)]
struct AgentRecord {
    agent_id: String,
    hostname: String,
    platform: String,
    agent_endpoint: String,  // "hostname:port" for Agent gRPC server
    max_storage_nodes: u32,
    current_storage_nodes: u32,
    last_heartbeat: u64,
    status: AgentStatus,
    storage_nodes: Vec<StorageNodeRecord>,
}

#[derive(Debug, Clone)]
struct StorageNodeRecord {
    node_id: String,
    endpoint: String,
    pid: u32,
    status: NodeStatus,
}

#[derive(Debug, Clone, PartialEq)]
enum AgentStatus {
    Healthy,
    Degraded,
    Offline,
}

impl AgentStatus {
    fn as_str(&self) -> &'static str {
        match self {
            AgentStatus::Healthy => "healthy",
            AgentStatus::Degraded => "degraded",
            AgentStatus::Offline => "offline",
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
enum NodeStatus {
    Starting,
    Running,
    Stopping,
    Stopped,
    Failed,
}

impl NodeStatus {
    fn as_str(&self) -> &'static str {
        match self {
            NodeStatus::Starting => "starting",
            NodeStatus::Running => "running",
            NodeStatus::Stopping => "stopping",
            NodeStatus::Stopped => "stopped",
            NodeStatus::Failed => "failed",
        }
    }
}

// ===== Grid Master Service =====

#[derive(Clone)]
struct GridMasterService {
    agents: Arc<RwLock<HashMap<String, AgentRecord>>>,
    agent_clients: Arc<RwLock<HashMap<String, agent::grid_agent_client::GridAgentClient<tonic::transport::Channel>>>>,
    events: Option<EventEmitter>,
}

impl GridMasterService {
    fn new() -> Self {
        Self {
            agents: Arc::new(RwLock::new(HashMap::new())),
            agent_clients: Arc::new(RwLock::new(HashMap::new())),
            events: None,
        }
    }
    
    fn new_with_events(events: EventEmitter) -> Self {
        Self {
            agents: Arc::new(RwLock::new(HashMap::new())),
            agent_clients: Arc::new(RwLock::new(HashMap::new())),
            events: Some(events),
        }
    }
    
    /// Get or create agent client
    async fn get_agent_client(
        &self,
        agent_id: &str,
    ) -> Result<agent::grid_agent_client::GridAgentClient<tonic::transport::Channel>, String> {
        // Check if client already exists
        {
            let clients = self.agent_clients.read().await;
            if let Some(client) = clients.get(agent_id) {
                return Ok(client.clone());
            }
        }
        
        // Get agent endpoint
        let endpoint = {
            let agents = self.agents.read().await;
            let agent = agents.get(agent_id)
                .ok_or_else(|| format!("Agent {} not found", agent_id))?;
            agent.agent_endpoint.clone()
        };
        
        // Create new client
        log::info!("📞 Creating gRPC client for agent {} at {}", agent_id, endpoint);
        let client = agent::grid_agent_client::GridAgentClient::connect(
            format!("http://{}", endpoint)
        )
        .await
        .map_err(|e| format!("Failed to connect to agent: {}", e))?;
        
        // Cache client
        self.agent_clients.write().await.insert(agent_id.to_string(), client.clone());
        
        Ok(client)
    }
    
    /// Get agent client with exponential backoff retry
    async fn get_agent_client_with_retry(
        &self,
        agent_id: &str,
        max_retries: u32,
    ) -> Result<agent::grid_agent_client::GridAgentClient<tonic::transport::Channel>, String> {
        let mut retry_count = 0;
        let mut delay_ms = 100;
        
        loop {
            match self.get_agent_client(agent_id).await {
                Ok(client) => return Ok(client),
                Err(e) => {
                    retry_count += 1;
                    
                    if retry_count >= max_retries {
                        return Err(format!("Max retries reached: {}", e));
                    }
                    
                    log::warn!(
                        "⚠️  Failed to connect to agent {} (attempt {}/{}): {}. Retrying in {}ms...",
                        agent_id, retry_count, max_retries, e, delay_ms
                    );
                    
                    // Invalidate cached client on error
                    self.agent_clients.write().await.remove(agent_id);
                    
                    tokio::time::sleep(tokio::time::Duration::from_millis(delay_ms)).await;
                    delay_ms *= 2; // Exponential backoff
                }
            }
        }
    }
    
    /// Check for stale agents (no heartbeat in 30 seconds)
    async fn check_agent_health(&self) {
        let mut agents = self.agents.write().await;
        let now = current_timestamp();
        
        for agent in agents.values_mut() {
            let seconds_since_heartbeat = now.saturating_sub(agent.last_heartbeat);
            
            if seconds_since_heartbeat > 30 {
                if agent.status != AgentStatus::Offline {
                    log::warn!("❌ Agent {} is offline (no heartbeat for {}s)", 
                              agent.agent_id, seconds_since_heartbeat);
                    
                    // Emit offline event
                    if let Some(events) = &self.events {
                        let last_seen = Utc.timestamp_opt(agent.last_heartbeat as i64, 0)
                            .single()
                            .unwrap_or_else(Utc::now);
                        events.emit(GridEvent::AgentOffline {
                            agent_id: agent.agent_id.clone(),
                            last_seen,
                            timestamp: Utc::now(),
                        });
                    }
                    
                    agent.status = AgentStatus::Offline;
                }
            } else if seconds_since_heartbeat > 15 {
                if agent.status != AgentStatus::Degraded {
                    log::warn!("⚠️  Agent {} is degraded (no heartbeat for {}s)", 
                              agent.agent_id, seconds_since_heartbeat);
                    
                    // Emit degraded event
                    if let Some(events) = &self.events {
                        events.emit(GridEvent::AgentDegraded {
                            agent_id: agent.agent_id.clone(),
                            seconds_since_heartbeat,
                            timestamp: Utc::now(),
                        });
                    }
                    
                    agent.status = AgentStatus::Degraded;
                }
            }
        }
    }
    
    /// Get cluster status
    async fn get_cluster_status_internal(&self) -> (u32, u32, u32, u32, &'static str) {
        let agents = self.agents.read().await;
        
        let total_agents = agents.len() as u32;
        let healthy_agents = agents.values()
            .filter(|a| a.status == AgentStatus::Healthy)
            .count() as u32;
        
        let total_storage_nodes: u32 = agents.values()
            .map(|a| a.current_storage_nodes)
            .sum();
        
        let running_storage_nodes: u32 = agents.values()
            .flat_map(|a| &a.storage_nodes)
            .filter(|n| n.status == NodeStatus::Running)
            .count() as u32;
        
        let status = if healthy_agents == 0 && total_agents > 0 {
            "critical"
        } else if healthy_agents < total_agents / 2 && total_agents > 0 {
            "degraded"
        } else {
            "healthy"
        };
        
        (total_agents, healthy_agents, total_storage_nodes, running_storage_nodes, status)
    }
}

#[tonic::async_trait]
impl grid::grid_master_server::GridMaster for GridMasterService {
    async fn register_agent(
        &self,
        request: Request<grid::AgentInfo>,
    ) -> Result<Response<grid::RegistrationResponse>, Status> {
        let info = request.into_inner();
        
        log::info!("📝 Agent registration request: {} ({})", info.agent_id, info.platform);
        
        let mut agents = self.agents.write().await;
        agents.insert(info.agent_id.clone(), AgentRecord {
            agent_id: info.agent_id.clone(),
            hostname: info.hostname.clone(),
            platform: info.platform.clone(),
            agent_endpoint: info.agent_endpoint.clone(),
            max_storage_nodes: info.max_storage_nodes,
            current_storage_nodes: 0,
            last_heartbeat: current_timestamp(),
            status: AgentStatus::Healthy,
            storage_nodes: Vec::new(),
        });
        
        log::info!(
            "✅ Agent registered: {} @ {} (total agents: {})",
            info.agent_id,
            info.agent_endpoint,
            agents.len()
        );
        
        // Emit registration event
        if let Some(events) = &self.events {
            events.emit(GridEvent::AgentRegistered {
                agent_id: info.agent_id.clone(),
                hostname: info.hostname.clone(),
                platform: info.platform.clone(),
                agent_endpoint: info.agent_endpoint.clone(),
                max_storage_nodes: info.max_storage_nodes,
                timestamp: Utc::now(),
            });
        }
        
        Ok(Response::new(grid::RegistrationResponse {
            success: true,
            master_version: env!("CARGO_PKG_VERSION").to_string(),
            error_message: String::new(),
        }))
    }
    
    async fn heartbeat(
        &self,
        request: Request<grid::HeartbeatRequest>,
    ) -> Result<Response<grid::HeartbeatResponse>, Status> {
        let req = request.into_inner();
        let now = current_timestamp();
        
        let mut agents = self.agents.write().await;
        if let Some(agent) = agents.get_mut(&req.agent_id) {
            let prev_heartbeat = agent.last_heartbeat;
            agent.last_heartbeat = now;
            agent.current_storage_nodes = req.storage_node_count;
            
            // Update status to healthy on heartbeat
            let was_degraded = agent.status != AgentStatus::Healthy;
            if was_degraded {
                log::info!("✅ Agent {} recovered", req.agent_id);
                
                // Calculate downtime for recovered event
                let downtime_seconds = now.saturating_sub(prev_heartbeat);
                
                // Emit recovery event
                if let Some(events) = &self.events {
                    events.emit(GridEvent::AgentRecovered {
                        agent_id: req.agent_id.clone(),
                        downtime_seconds,
                        timestamp: Utc::now(),
                    });
                }
                
                agent.status = AgentStatus::Healthy;
            }
            
            log::debug!("💓 Heartbeat from {} (nodes: {})", req.agent_id, req.storage_node_count);
        } else {
            log::warn!("❌ Heartbeat from unregistered agent: {}", req.agent_id);
            return Err(Status::not_found("Agent not registered"));
        }
        
        Ok(Response::new(grid::HeartbeatResponse {
            acknowledged: true,
            timestamp: current_timestamp(),
        }))
    }
    
    async fn unregister_agent(
        &self,
        request: Request<grid::AgentId>,
    ) -> Result<Response<grid::Empty>, Status> {
        let req = request.into_inner();
        
        let mut agents = self.agents.write().await;
        if agents.remove(&req.agent_id).is_some() {
            log::info!("👋 Agent unregistered: {}", req.agent_id);
            
            // Emit unregister event
            if let Some(events) = &self.events {
                events.emit(GridEvent::AgentUnregistered {
                    agent_id: req.agent_id.clone(),
                    timestamp: Utc::now(),
                });
            }
            
            Ok(Response::new(grid::Empty {}))
        } else {
            Err(Status::not_found("Agent not found"))
        }
    }
    
    async fn spawn_storage_node(
        &self,
        request: Request<grid::SpawnRequest>,
    ) -> Result<Response<grid::SpawnResponse>, Status> {
        let req = request.into_inner();
        
        log::info!("📦 Spawn storage node request for agent {}", req.agent_id);
        
        // Verify agent exists and is healthy
        {
            let agents = self.agents.read().await;
            let agent = agents.get(&req.agent_id)
                .ok_or_else(|| Status::not_found("Agent not registered"))?;
            
            if agent.status == AgentStatus::Offline {
                return Err(Status::unavailable("Agent is offline"));
            }
        }
        
        // Generate node ID
        let node_id = format!("node-{}", uuid::Uuid::new_v4());
        
        // Emit spawn requested event
        if let Some(events) = &self.events {
            events.emit(GridEvent::SpawnRequested {
                node_id: node_id.clone(),
                agent_id: req.agent_id.clone(),
                port: req.port,
                storage_path: req.storage_path.clone(),
                memory_limit_mb: req.memory_limit_mb,
                timestamp: Utc::now(),
            });
        }
        
        // Get agent client with retry
        let mut agent_client = match self.get_agent_client_with_retry(&req.agent_id, 3).await {
            Ok(client) => client,
            Err(e) => {
                log::error!("❌ Failed to connect to agent {}: {}", req.agent_id, e);
                return Err(Status::unavailable(format!("Failed to connect to agent: {}", e)));
            }
        };
        
        // Forward spawn request to agent
        log::info!("🔀 Forwarding spawn request to agent {} for node {}", req.agent_id, node_id);
        
        let spawn_request = agent::SpawnNodeRequest {
            node_id: node_id.clone(),
            storage_path: req.storage_path.clone(),
            port: req.port,
            memory_limit_mb: req.memory_limit_mb,
        };
        
        match tokio::time::timeout(
            tokio::time::Duration::from_secs(30),
            agent_client.spawn_node(spawn_request)
        ).await {
            Ok(Ok(response)) => {
                let resp = response.into_inner();
                
                if resp.success {
                    log::info!(
                        "✅ Agent {} spawned node {} (PID: {}, Port: {})",
                        req.agent_id,
                        resp.node_id,
                        resp.pid,
                        resp.port
                    );
                    
                    // Emit spawn succeeded event
                    if let Some(events) = &self.events {
                        events.emit(GridEvent::SpawnSucceeded {
                            node_id: resp.node_id.clone(),
                            agent_id: req.agent_id.clone(),
                            pid: resp.pid,
                            port: resp.port,
                            timestamp: Utc::now(),
                        });
                    }
                    
                    // Update agent record with new storage node
                    {
                        let mut agents = self.agents.write().await;
                        if let Some(agent) = agents.get_mut(&req.agent_id) {
                            agent.storage_nodes.push(StorageNodeRecord {
                                node_id: resp.node_id.clone(),
                                endpoint: format!("{}:{}", agent.hostname, resp.port),
                                pid: resp.pid,
                                status: NodeStatus::Running,
                            });
                        }
                    }
                    
                    Ok(Response::new(grid::SpawnResponse {
                        node_id: resp.node_id,
                        endpoint: format!("localhost:{}", resp.port),
                        success: true,
                        error_message: String::new(),
                    }))
                } else {
                    log::error!("❌ Agent {} failed to spawn node: {}", req.agent_id, resp.error_message);
                    
                    // Emit spawn failed event
                    if let Some(events) = &self.events {
                        events.emit(GridEvent::SpawnFailed {
                            node_id: node_id.clone(),
                            agent_id: req.agent_id.clone(),
                            error: resp.error_message.clone(),
                            timestamp: Utc::now(),
                        });
                    }
                    
                    Ok(Response::new(grid::SpawnResponse {
                        node_id: node_id.clone(),
                        endpoint: String::new(),
                        success: false,
                        error_message: resp.error_message,
                    }))
                }
            }
            Ok(Err(e)) => {
                let error_msg = format!("Agent communication error: {}", e);
                log::error!("❌ gRPC call to agent {} failed: {}", req.agent_id, e);
                
                // Emit spawn failed event
                if let Some(events) = &self.events {
                    events.emit(GridEvent::SpawnFailed {
                        node_id: node_id.clone(),
                        agent_id: req.agent_id.clone(),
                        error: error_msg.clone(),
                        timestamp: Utc::now(),
                    });
                }
                
                Err(Status::internal(error_msg))
            }
            Err(_) => {
                let error_msg = "Request timeout".to_string();
                log::error!("⏱️ Timeout spawning node on agent {}", req.agent_id);
                
                // Emit spawn failed event
                if let Some(events) = &self.events {
                    events.emit(GridEvent::SpawnFailed {
                        node_id: node_id.clone(),
                        agent_id: req.agent_id.clone(),
                        error: error_msg.clone(),
                        timestamp: Utc::now(),
                    });
                }
                
                Err(Status::deadline_exceeded(error_msg))
            }
        }
    }
    
    async fn stop_storage_node(
        &self,
        request: Request<grid::StopRequest>,
    ) -> Result<Response<grid::StopResponse>, Status> {
        let req = request.into_inner();
        
        log::info!("🛑 Stop storage node request: {} from agent {}", req.node_id, req.agent_id);
        
        // Verify agent exists
        {
            let agents = self.agents.read().await;
            if !agents.contains_key(&req.agent_id) {
                return Err(Status::not_found("Agent not registered"));
            }
        }
        
        // Get agent client with retry
        let mut agent_client = match self.get_agent_client_with_retry(&req.agent_id, 3).await {
            Ok(client) => client,
            Err(e) => {
                log::error!("❌ Failed to connect to agent {}: {}", req.agent_id, e);
                return Err(Status::unavailable(format!("Failed to connect to agent: {}", e)));
            }
        };
        
        // Emit stop requested event
        if let Some(events) = &self.events {
            events.emit(GridEvent::StopRequested {
                node_id: req.node_id.clone(),
                agent_id: req.agent_id.clone(),
                timestamp: Utc::now(),
            });
        }
        
        // Forward stop request to agent
        log::info!("🔀 Forwarding stop request to agent {} for node {}", req.agent_id, req.node_id);
        
        let stop_request = agent::StopNodeRequest {
            node_id: req.node_id.clone(),
        };
        
        match tokio::time::timeout(
            tokio::time::Duration::from_secs(10),
            agent_client.stop_node(stop_request)
        ).await {
            Ok(Ok(response)) => {
                let resp = response.into_inner();
                
                if resp.success {
                    log::info!("✅ Agent {} stopped node {}", req.agent_id, req.node_id);
                    
                    // Emit stop succeeded event
                    if let Some(events) = &self.events {
                        events.emit(GridEvent::StopSucceeded {
                            node_id: req.node_id.clone(),
                            agent_id: req.agent_id.clone(),
                            timestamp: Utc::now(),
                        });
                    }
                    
                    // Update agent record - remove or mark as stopped
                    {
                        let mut agents = self.agents.write().await;
                        if let Some(agent) = agents.get_mut(&req.agent_id) {
                            if let Some(node) = agent.storage_nodes.iter_mut().find(|n| n.node_id == req.node_id) {
                                node.status = NodeStatus::Stopped;
                            }
                        }
                    }
                    
                    Ok(Response::new(grid::StopResponse {
                        success: true,
                        error_message: String::new(),
                    }))
                } else {
                    log::error!("❌ Agent {} failed to stop node: {}", req.agent_id, resp.error_message);
                    
                    // Emit stop failed event
                    if let Some(events) = &self.events {
                        events.emit(GridEvent::StopFailed {
                            node_id: req.node_id.clone(),
                            agent_id: req.agent_id.clone(),
                            error: resp.error_message.clone(),
                            timestamp: Utc::now(),
                        });
                    }
                    
                    Ok(Response::new(grid::StopResponse {
                        success: false,
                        error_message: resp.error_message,
                    }))
                }
            }
            Ok(Err(e)) => {
                let error_msg = format!("Agent communication error: {}", e);
                log::error!("❌ gRPC call to agent {} failed: {}", req.agent_id, e);
                
                // Emit stop failed event
                if let Some(events) = &self.events {
                    events.emit(GridEvent::StopFailed {
                        node_id: req.node_id.clone(),
                        agent_id: req.agent_id.clone(),
                        error: error_msg.clone(),
                        timestamp: Utc::now(),
                    });
                }
                
                Err(Status::internal(error_msg))
            }
            Err(_) => {
                let error_msg = "Request timeout".to_string();
                log::error!("⏱️ Timeout stopping node {} on agent {}", req.node_id, req.agent_id);
                
                // Emit stop failed event
                if let Some(events) = &self.events {
                    events.emit(GridEvent::StopFailed {
                        node_id: req.node_id.clone(),
                        agent_id: req.agent_id.clone(),
                        error: error_msg.clone(),
                        timestamp: Utc::now(),
                    });
                }
                
                Err(Status::deadline_exceeded(error_msg))
            }
        }
    }
    
    async fn get_storage_node_status(
        &self,
        request: Request<grid::NodeId>,
    ) -> Result<Response<grid::NodeStatus>, Status> {
        let req = request.into_inner();
        
        log::debug!("❓ Status query for node {}", req.node_id);
        
        // Search for node across all agents to find which agent owns it
        let (agent_id, node_cached) = {
            let agents = self.agents.read().await;
            let mut result = None;
            
            for agent in agents.values() {
                if let Some(node) = agent.storage_nodes.iter().find(|n| n.node_id == req.node_id) {
                    result = Some((agent.agent_id.clone(), node.clone()));
                    break;
                }
            }
            
            result.ok_or_else(|| Status::not_found("Node not found"))?
        };
        
        // Query agent for real-time status
        match self.get_agent_client(&agent_id).await {
            Ok(mut client) => {
                let status_request = agent::NodeStatusRequest {
                    node_id: req.node_id.clone(),
                };
                
                match tokio::time::timeout(
                    tokio::time::Duration::from_secs(5),
                    client.get_node_status(status_request)
                ).await {
                    Ok(Ok(response)) => {
                        let resp = response.into_inner();
                        
                        // Construct endpoint from agent hostname and port
                        let endpoint = {
                            let agents = self.agents.read().await;
                            if let Some(agent) = agents.get(&agent_id) {
                                format!("{}:{}", agent.hostname, resp.port)
                            } else {
                                format!("unknown:{}", resp.port)
                            }
                        };
                        
                        Ok(Response::new(grid::NodeStatus {
                            node_id: resp.node_id,
                            status: resp.status,
                            pid: resp.pid,
                            endpoint,
                        }))
                    }
                    Ok(Err(e)) => {
                        log::warn!("⚠️ Failed to query agent for node status: {}", e);
                        // Fallback to cached status
                        Ok(Response::new(grid::NodeStatus {
                            node_id: node_cached.node_id,
                            status: node_cached.status.as_str().to_string(),
                            pid: node_cached.pid,
                            endpoint: node_cached.endpoint,
                        }))
                    }
                    Err(_) => {
                        log::warn!("⏱️ Timeout querying agent for node status");
                        // Fallback to cached status
                        Ok(Response::new(grid::NodeStatus {
                            node_id: node_cached.node_id,
                            status: node_cached.status.as_str().to_string(),
                            pid: node_cached.pid,
                            endpoint: node_cached.endpoint,
                        }))
                    }
                }
            }
            Err(e) => {
                log::warn!("⚠️ Failed to connect to agent: {}", e);
                // Fallback to cached status
                Ok(Response::new(grid::NodeStatus {
                    node_id: node_cached.node_id,
                    status: node_cached.status.as_str().to_string(),
                    pid: node_cached.pid,
                    endpoint: node_cached.endpoint,
                }))
            }
        }
    }
    
    async fn list_agents(
        &self,
        _request: Request<grid::Empty>,
    ) -> Result<Response<grid::AgentList>, Status> {
        log::debug!("📋 List agents request");
        
        let agents = self.agents.read().await;
        
        let agent_records: Vec<grid::AgentRecord> = agents.values().map(|a| {
            grid::AgentRecord {
                agent_id: a.agent_id.clone(),
                hostname: a.hostname.clone(),
                platform: a.platform.clone(),
                status: a.status.as_str().to_string(),
                max_storage_nodes: a.max_storage_nodes,
                current_storage_nodes: a.current_storage_nodes,
                last_heartbeat: a.last_heartbeat,
                storage_nodes: a.storage_nodes.iter().map(|n| {
                    grid::NodeStatus {
                        node_id: n.node_id.clone(),
                        status: n.status.as_str().to_string(),
                        pid: n.pid,
                        endpoint: n.endpoint.clone(),
                    }
                }).collect(),
            }
        }).collect();
        
        Ok(Response::new(grid::AgentList {
            agents: agent_records,
        }))
    }
    
    async fn get_cluster_status(
        &self,
        _request: Request<grid::Empty>,
    ) -> Result<Response<grid::ClusterStatus>, Status> {
        log::debug!("📊 Cluster status request");
        
        let (total_agents, healthy_agents, total_storage_nodes, running_storage_nodes, status) =
            self.get_cluster_status_internal().await;
        
        Ok(Response::new(grid::ClusterStatus {
            total_agents,
            healthy_agents,
            total_storage_nodes,
            running_storage_nodes,
            status: status.to_string(),
        }))
    }
}

// ===== Health Monitor =====

async fn health_monitor_loop(service: GridMasterService) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(10));
    
    loop {
        interval.tick().await;
        service.check_agent_health().await;
        
        // Log cluster status
        let (total, healthy, storage_total, storage_running, status) =
            service.get_cluster_status_internal().await;
        
        log::info!(
            "📊 Cluster: {} agents ({} healthy), {} storage nodes ({} running) - {}",
            total, healthy, storage_total, storage_running, status
        );
    }
}

// ===== Main =====

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();
    
    let grpc_addr = "0.0.0.0:7002".parse::<std::net::SocketAddr>()?;
    let http_addr = "0.0.0.0:7001".parse::<std::net::SocketAddr>()?;  // Binary distribution HTTP server
    
    log::info!("🚀 Sutra Grid Master v{} starting", env!("CARGO_PKG_VERSION"));
    log::info!("  📡 gRPC: {}", grpc_addr);
    log::info!("  🌐 HTTP: {}", http_addr);
    
    // Initialize event storage connection (optional)
    let event_storage = std::env::var("EVENT_STORAGE")
        .unwrap_or_else(|_| "http://localhost:50052".to_string());
    
    let service = match sutra_grid_events::init_events(event_storage.clone()).await {
        Ok(events) => {
            log::info!("📊 Event emission enabled (storage: {})", event_storage);
            GridMasterService::new_with_events(events)
        }
        Err(e) => {
            log::warn!("⚠️  Event emission disabled: {}. Continuing without events.", e);
            GridMasterService::new()
        }
    };
    
    // Initialize binary distribution system
    let binaries_dir = PathBuf::from(std::env::var("BINARIES_DIR")
        .unwrap_or_else(|_| "./binaries".to_string()));
    let binary_distribution = binary_server::BinaryDistribution::new(binaries_dir.clone());
    
    // Auto-register any existing binaries
    auto_register_binaries(&binary_distribution, &binaries_dir).await?;
    
    log::info!("📡 Listening for agent connections...");
    
    // Start health monitor
    let monitor_service = service.clone();
    tokio::spawn(async move {
        health_monitor_loop(monitor_service).await;
    });
    
    // Start HTTP binary distribution server
    let http_router = binary_server::create_router(binary_distribution, binaries_dir);
    let http_addr_clone = http_addr;
    let http_server = tokio::spawn(async move {
        log::info!("🌐 HTTP binary server started on {}", http_addr_clone);
        axum::serve(
            tokio::net::TcpListener::bind(http_addr_clone).await.unwrap(),
            http_router
        )
        .await
        .unwrap();
    });
    
    // Start gRPC server
    let grpc_server = tokio::spawn(async move {
        Server::builder()
            .add_service(grid::grid_master_server::GridMasterServer::new(service))
            .serve(grpc_addr)
            .await
            .unwrap();
    });
    
    // Wait for both servers
    tokio::select! {
        _ = http_server => log::error!("HTTP server stopped"),
        _ = grpc_server => log::error!("gRPC server stopped"),
    }
    
    Ok(())
}

// ===== Utilities =====

fn current_timestamp() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

/// Auto-register binaries found in the binaries directory
/// Expected filename format: storage-server-{version}-{platform}-{arch}
async fn auto_register_binaries(
    distribution: &binary_server::BinaryDistribution,
    binaries_dir: &PathBuf,
) -> Result<(), Box<dyn std::error::Error>> {
    if !binaries_dir.exists() {
        std::fs::create_dir_all(binaries_dir)?;
        log::info!("📂 Created binaries directory: {:?}", binaries_dir);
        return Ok(());
    }
    
    let entries = std::fs::read_dir(binaries_dir)?;
    let mut registered_count = 0;
    
    for entry in entries {
        let entry = entry?;
        let path = entry.path();
        
        if !path.is_file() {
            continue;
        }
        
        let filename = path.file_name()
            .and_then(|n| n.to_str())
            .unwrap_or("");
        
        // Parse filename: storage-server-{version}-{platform}-{arch}
        if let Some(parsed) = parse_binary_filename(filename) {
            let (version, platform, arch) = parsed;
            
            match distribution.register_binary(
                version.clone(),
                platform.clone(),
                arch.clone(),
                path.clone(),
            ).await {
                Ok(_) => {
                    registered_count += 1;
                    log::info!("✅ Auto-registered: {} {} {}", version, platform, arch);
                }
                Err(e) => {
                    log::warn!("⚠️  Failed to register {}: {}", filename, e);
                }
            }
        } else {
            log::debug!("Skipping non-binary file: {}", filename);
        }
    }
    
    if registered_count > 0 {
        log::info!("📦 Auto-registered {} binaries", registered_count);
    } else {
        log::info!("📂 No binaries found in directory (add with format: storage-server-VERSION-PLATFORM-ARCH)");
    }
    
    Ok(())
}

/// Parse binary filename into (version, platform, arch)
fn parse_binary_filename(filename: &str) -> Option<(String, String, String)> {
    // Expected format: storage-server-{version}-{platform}-{arch}
    if !filename.starts_with("storage-server-") {
        return None;
    }
    
    let parts: Vec<&str> = filename
        .strip_prefix("storage-server-")?
        .split('-')
        .collect();
    
    if parts.len() >= 3 {
        Some((
            parts[0].to_string(),
            parts[1].to_string(),
            parts[2].to_string(),
        ))
    } else {
        None
    }
}
