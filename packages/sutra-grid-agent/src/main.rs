use serde::Deserialize;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use tokio::process::Command;
use tonic::transport::Channel;
use chrono::Utc;
use sutra_grid_events::{EventEmitter, GridEvent};

// Include generated protobuf code
pub mod grid {
    tonic::include_proto!("grid");
}

pub mod agent {
    tonic::include_proto!("agent");
}

// ===== Configuration =====

#[derive(Debug, Clone, Deserialize)]
struct Config {
    agent: AgentConfig,
    storage: StorageConfig,
    monitoring: MonitoringConfig,
}

#[derive(Debug, Clone, Deserialize)]
struct AgentConfig {
    agent_id: String,
    master_host: String,
    platform: String,
    max_storage_nodes: u32,
    agent_port: u16,  // Port for Agent gRPC server (Master → Agent commands)
}

#[derive(Debug, Clone, Deserialize)]
struct StorageConfig {
    binary_path: String,
    data_path: String,
    default_memory_mb: u64,
    default_port_range_start: u32,
}

#[derive(Debug, Clone, Deserialize)]
struct MonitoringConfig {
    heartbeat_interval_secs: u64,
    health_check_interval_secs: u64,
    restart_failed_nodes: bool,
}

impl Config {
    fn load(path: &str) -> anyhow::Result<Self> {
        let content = std::fs::read_to_string(path)?;
        let config: Config = toml::from_str(&content)?;
        Ok(config)
    }
}

// ===== Storage Process Tracking =====

#[derive(Debug)]
struct StorageProcess {
    node_id: String,
    port: u32,
    pid: u32,
    storage_path: String,
    started_at: u64,
    restart_count: u32,
}

// ===== Agent =====

#[derive(Clone)]
struct Agent {
    config: Config,
    master_client: grid::grid_master_client::GridMasterClient<Channel>,
    storage_processes: Arc<RwLock<HashMap<String, StorageProcess>>>,
    next_port: Arc<RwLock<u32>>,
    events: Option<EventEmitter>,
}

// ===== Agent gRPC Service (receives commands from Master) =====

#[tonic::async_trait]
impl agent::grid_agent_server::GridAgent for Agent {
    async fn spawn_node(
        &self,
        request: tonic::Request<agent::SpawnNodeRequest>,
    ) -> Result<tonic::Response<agent::SpawnNodeResponse>, tonic::Status> {
        let req = request.into_inner();
        
        log::info!("📨 Received spawn request from Master: {}", req.node_id);
        
        match self.spawn_storage_node(req.node_id.clone()).await {
            Ok((port, pid)) => {
                log::info!("✅ Spawned node {} (Port: {}, PID: {})", req.node_id, port, pid);
                Ok(tonic::Response::new(agent::SpawnNodeResponse {
                    success: true,
                    node_id: req.node_id,
                    port,
                    pid,
                    error_message: String::new(),
                }))
            }
            Err(e) => {
                log::error!("❌ Failed to spawn {}: {}", req.node_id, e);
                Ok(tonic::Response::new(agent::SpawnNodeResponse {
                    success: false,
                    node_id: req.node_id,
                    port: 0,
                    pid: 0,
                    error_message: e.to_string(),
                }))
            }
        }
    }
    
    async fn stop_node(
        &self,
        request: tonic::Request<agent::StopNodeRequest>,
    ) -> Result<tonic::Response<agent::StopNodeResponse>, tonic::Status> {
        let req = request.into_inner();
        
        log::info!("🛑 Received stop request: {}", req.node_id);
        
        match self.stop_storage_node(&req.node_id).await {
            Ok(_) => {
                log::info!("✅ Storage node {} stopped successfully", req.node_id);
                Ok(tonic::Response::new(agent::StopNodeResponse {
                    success: true,
                    error_message: String::new(),
                }))
            }
            Err(e) => {
                log::error!("❌ Failed to stop node {}: {}", req.node_id, e);
                Ok(tonic::Response::new(agent::StopNodeResponse {
                    success: false,
                    error_message: e.to_string(),
                }))
            }
        }
    }
    
    async fn get_node_status(
        &self,
        request: tonic::Request<agent::NodeStatusRequest>,
    ) -> Result<tonic::Response<agent::NodeStatusResponse>, tonic::Status> {
        let req = request.into_inner();
        
        let processes = self.storage_processes.read().await;
        if let Some(process) = processes.get(&req.node_id) {
            Ok(tonic::Response::new(agent::NodeStatusResponse {
                node_id: process.node_id.clone(),
                status: "running".to_string(),
                pid: process.pid,
                port: process.port,
                storage_path: process.storage_path.clone(),
                started_at: process.started_at,
                restart_count: process.restart_count,
            }))
        } else {
            Err(tonic::Status::not_found("Node not found"))
        }
    }
    
    async fn list_nodes(
        &self,
        _request: tonic::Request<agent::ListNodesRequest>,
    ) -> Result<tonic::Response<agent::ListNodesResponse>, tonic::Status> {
        let processes = self.storage_processes.read().await;
        
        let nodes: Vec<agent::NodeStatusResponse> = processes.values().map(|p| {
            agent::NodeStatusResponse {
                node_id: p.node_id.clone(),
                status: "running".to_string(),
                pid: p.pid,
                port: p.port,
                storage_path: p.storage_path.clone(),
                started_at: p.started_at,
                restart_count: p.restart_count,
            }
        }).collect();
        
        Ok(tonic::Response::new(agent::ListNodesResponse { nodes }))
    }
}

impl Agent {
    async fn new(config: Config, events: Option<EventEmitter>) -> anyhow::Result<Self> {
        log::info!("🔌 Connecting to Master at {}", config.agent.master_host);
        
        let master_client = grid::grid_master_client::GridMasterClient::connect(
            format!("http://{}", config.agent.master_host)
        ).await?;
        
        log::info!("✅ Connected to Master");
        
        let next_port = config.storage.default_port_range_start;
        
        Ok(Self {
            config,
            master_client,
            storage_processes: Arc::new(RwLock::new(HashMap::new())),
            next_port: Arc::new(RwLock::new(next_port)),
            events,
        })
    }
    
    /// Spawn a storage node process
    async fn spawn_storage_node(
        &self,
        node_id: String,
    ) -> anyhow::Result<(u32, u32)> {  // Returns (port, pid)
        let processes = self.storage_processes.read().await;
        if processes.len() >= self.config.agent.max_storage_nodes as usize {
            return Err(anyhow::anyhow!("Max storage nodes reached"));
        }
        drop(processes);
        
        // Get next available port
        let port = {
            let mut next_port = self.next_port.write().await;
            let port = *next_port;
            *next_port += 1;
            port
        };
        
        // Create storage path
        let storage_path = format!("{}/{}", self.config.storage.data_path, node_id);
        std::fs::create_dir_all(&storage_path)?;
        
        log::info!("📦 Spawning storage node {} on port {}", node_id, port);
        
        // Spawn process
        let mut cmd = Command::new(&self.config.storage.binary_path);
        cmd.arg("--port").arg(port.to_string())
           .arg("--storage-path").arg(&storage_path)
           .arg("--node-id").arg(&node_id)
           .stdout(std::process::Stdio::null())  // Don't clutter logs
           .stderr(std::process::Stdio::null());
        
        let mut child = cmd.spawn()?;
        let pid = child.id().ok_or_else(|| anyhow::anyhow!("Failed to get PID"))?;
        
        log::info!("✅ Storage node {} spawned (PID: {}, Port: {})", node_id, pid, port);
        
        // Track process
        let process = StorageProcess {
            node_id: node_id.clone(),
            port,
            pid,
            storage_path: storage_path.clone(),
            started_at: current_timestamp(),
            restart_count: 0,
        };
        
        self.storage_processes.write().await.insert(node_id.clone(), process);
        
        // Monitor process in background
        let processes = Arc::clone(&self.storage_processes);
        let node_id_clone = node_id.clone();
        tokio::spawn(async move {
            let status = child.wait().await;
            log::warn!("⚠️  Storage node {} exited: {:?}", node_id_clone, status);
            
            // Remove from tracking
            processes.write().await.remove(&node_id_clone);
        });
        
        Ok((port, pid))
    }
    
    /// Stop a storage node process
    async fn stop_storage_node(&self, node_id: &str) -> anyhow::Result<()> {
        let mut processes = self.storage_processes.write().await;
        
        if let Some(process) = processes.get(node_id) {
            let pid = process.pid;
            log::info!("🛑 Stopping storage node {} (PID: {})", node_id, pid);
            
            // Try to terminate the process gracefully
            #[cfg(unix)]
            {
                use std::process::Command;
                
                // First try SIGTERM (graceful shutdown)
                match Command::new("kill")
                    .arg("-TERM")
                    .arg(pid.to_string())
                    .status() {
                    Ok(status) if status.success() => {
                        log::info!("📴 Sent SIGTERM to process {}", pid);
                        
                        // Wait a bit for graceful shutdown
                        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
                        
                        // Check if process is still alive
                        if check_process_alive(pid) {
                            log::warn!("⚠️  Process {} still alive, sending SIGKILL", pid);
                            let _ = Command::new("kill")
                                .arg("-KILL")
                                .arg(pid.to_string())
                                .status();
                        }
                    }
                    _ => {
                        log::warn!("⚠️  SIGTERM failed, trying SIGKILL");
                        let _ = Command::new("kill")
                            .arg("-KILL")
                            .arg(pid.to_string())
                            .status();
                    }
                }
            }
            
            #[cfg(not(unix))]
            {
                log::warn!("Process termination not implemented for this platform");
                return Err(anyhow::anyhow!("Process termination not supported on this platform"));
            }
            
            // Remove from tracking
            processes.remove(node_id);
            log::info!("✅ Storage node {} removed from tracking", node_id);
            
            Ok(())
        } else {
            Err(anyhow::anyhow!("Node {} not found", node_id))
        }
    }
    
    /// Monitor storage processes and restart if needed
    async fn monitor_storage_nodes(agent_ref: Arc<RwLock<Agent>>) {
        let mut interval = tokio::time::interval(
            tokio::time::Duration::from_secs(10)
        );
        
        log::info!("🔍 Starting storage node monitor");
        
        loop {
            interval.tick().await;
            
            // Collect crashed nodes and emit events
            let crashed_nodes: Vec<(String, u32, String)> = {
                let agent = agent_ref.read().await;
                let mut processes = agent.storage_processes.write().await;
                let mut crashed = Vec::new();
                
                for (node_id, process) in processes.iter_mut() {
                    let is_alive = check_process_alive(process.pid);
                    if !is_alive {
                        log::warn!("❌ Node {} (PID {}) crashed!", node_id, process.pid);
                        crashed.push((
                            node_id.clone(),
                            process.restart_count,
                            agent.config.agent.agent_id.clone(),
                        ));
                    }
                }
                crashed
            };
            
            // Emit crash events
            for (node_id, restart_count, agent_id) in &crashed_nodes {
                let agent = agent_ref.read().await;
                if let Some(events) = &agent.events {
                    events.emit(GridEvent::NodeCrashed {
                        node_id: node_id.clone(),
                        agent_id: agent_id.clone(),
                        exit_code: None,  // Can't get exit code post-crash
                        timestamp: Utc::now(),
                    });
                }
            }
            
            // Restart failed nodes
            for (node_id, restart_count, agent_id) in crashed_nodes {
                let agent = agent_ref.read().await;
                let restart_enabled = agent.config.monitoring.restart_failed_nodes;
                let max_restarts = 3;
                
                if restart_enabled && restart_count < max_restarts {
                    drop(agent);  // Drop read lock
                    
                    log::warn!("🔄 Restarting node {} (attempt {})", node_id, restart_count + 1);
                    
                    let mut agent = agent_ref.write().await;
                    
                    // Update restart count
                    if let Some(process) = agent.storage_processes.write().await.get_mut(&node_id) {
                        process.restart_count += 1;
                    }
                    
                    // Restart the node
                    match agent.spawn_storage_node(node_id.clone()).await {
                        Ok((port, new_pid)) => {
                            log::info!("✅ Node {} restarted (new PID: {})", node_id, new_pid);
                            
                            // Emit restart event
                            if let Some(events) = &agent.events {
                                events.emit(GridEvent::NodeRestarted {
                                    node_id: node_id.clone(),
                                    agent_id,
                                    restart_count: restart_count + 1,
                                    new_pid,
                                    timestamp: Utc::now(),
                                });
                            }
                        }
                        Err(e) => {
                            log::error!("❌ Failed to restart node {}: {}", node_id, e);
                        }
                    }
                }
            }
        }
    }
    
    async fn register(&mut self) -> anyhow::Result<()> {
        log::info!("📝 Registering with Master...");
        
        let hostname = hostname::get()?
            .to_string_lossy()
            .to_string();
        
        let agent_endpoint = format!("{}:{}", hostname, self.config.agent.agent_port);
        
        let request = grid::AgentInfo {
            agent_id: self.config.agent.agent_id.clone(),
            hostname: hostname.clone(),
            platform: self.config.agent.platform.clone(),
            max_storage_nodes: self.config.agent.max_storage_nodes,
            version: env!("CARGO_PKG_VERSION").to_string(),
            agent_endpoint,
        };
        
        let response = self.master_client.register_agent(request).await?;
        let result = response.into_inner();
        
        if result.success {
            log::info!(
                "✅ Registered with Master (Master v{}, Agent: {}, Host: {})",
                result.master_version,
                self.config.agent.agent_id,
                hostname
            );
            Ok(())
        } else {
            Err(anyhow::anyhow!("Registration failed: {}", result.error_message))
        }
    }
    
    async fn heartbeat_loop(mut self) {
        let interval_secs = self.config.monitoring.heartbeat_interval_secs;
        let mut interval = tokio::time::interval(
            tokio::time::Duration::from_secs(interval_secs)
        );
        
        log::info!("💓 Starting heartbeat loop (interval: {}s)", interval_secs);
        
        let mut heartbeat_count = 0u64;
        
        loop {
            interval.tick().await;
            
            let node_count = self.storage_processes.read().await.len() as u32;
            
            let request = grid::HeartbeatRequest {
                agent_id: self.config.agent.agent_id.clone(),
                storage_node_count: node_count,
                timestamp: current_timestamp(),
            };
            
            match self.master_client.heartbeat(request).await {
                Ok(response) => {
                    heartbeat_count += 1;
                    let ack = response.into_inner();
                    
                    if heartbeat_count % 12 == 0 {  // Log every minute (12 * 5s)
                        log::info!(
                            "💓 Heartbeat #{} acknowledged (Master time: {})",
                            heartbeat_count,
                            ack.timestamp
                        );
                    } else {
                        log::debug!("💓 Heartbeat #{} sent", heartbeat_count);
                    }
                }
                Err(e) => {
                    log::error!("❌ Heartbeat failed: {}", e);
                    log::warn!("⚠️  Connection to Master lost, will retry...");
                    
                    // Try to reconnect
                    tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
                    
                    match grid::grid_master_client::GridMasterClient::connect(
                        format!("http://{}", self.config.agent.master_host)
                    ).await {
                        Ok(new_client) => {
                            log::info!("✅ Reconnected to Master");
                            self.master_client = new_client;
                            
                            // Re-register
                            if let Err(e) = self.register().await {
                                log::error!("❌ Re-registration failed: {}", e);
                            }
                        }
                        Err(e) => {
                            log::error!("❌ Reconnection failed: {}", e);
                        }
                    }
                }
            }
        }
    }
}

// ===== Main =====

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();
    
    log::info!("🚀 Sutra Grid Agent v{} starting...", env!("CARGO_PKG_VERSION"));
    
    // Load config
    let config_path = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "agent-config.toml".to_string());
    
    log::info!("📄 Loading config from {}", config_path);
    let config = Config::load(&config_path)?;
    
    log::info!(
        "⚙️  Config: Agent ID: {}, Platform: {}, Max Nodes: {}",
        config.agent.agent_id,
        config.agent.platform,
        config.agent.max_storage_nodes
    );
    
    // Initialize event storage connection (optional)
    let event_storage = std::env::var("EVENT_STORAGE")
        .unwrap_or_else(|_| "http://localhost:50052".to_string());
    
    let events = match sutra_grid_events::init_events(event_storage.clone()).await {
        Ok(events) => {
            log::info!("📊 Event emission enabled (storage: {})", event_storage);
            Some(events)
        }
        Err(e) => {
            log::warn!("⚠️  Event emission disabled: {}. Continuing without events.", e);
            None
        }
    };
    
    // Create agent
    let mut agent = Agent::new(config, events).await?;
    
    // Register with Master
    agent.register().await?;
    
    // Agent is now cloneable, prepare for concurrent tasks
    let agent_port = agent.config.agent.agent_port;
    let agent_addr = format!("0.0.0.0:{}", agent_port).parse()?;
    
    log::info!("📻 Starting Agent gRPC server on port {}...", agent_port);
    
    // Start Agent gRPC server (receives commands from Master)
    let agent_service = agent.clone();
    let grpc_server = tokio::spawn(async move {
        tonic::transport::Server::builder()
            .add_service(agent::grid_agent_server::GridAgentServer::new(agent_service))
            .serve(agent_addr)
            .await
    });
    
    log::info!("✅ Agent gRPC server started on port {}", agent_port);
    
    // Start storage node monitor
    let monitor_agent = agent.clone();
    tokio::spawn(async move {
        // Wrap in Arc<RwLock> for monitor
        let agent_arc = Arc::new(RwLock::new(monitor_agent));
        Agent::monitor_storage_nodes(agent_arc).await;
    });
    
    // Start heartbeat loop (runs forever)
    agent.heartbeat_loop().await;
    
    Ok(())
}

// ===== Utilities =====

fn current_timestamp() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

/// Check if a process with given PID is still alive
fn check_process_alive(pid: u32) -> bool {
    // On Unix, send signal 0 to check if process exists
    #[cfg(unix)]
    {
        use std::process::Command;
        Command::new("kill")
            .arg("-0")
            .arg(pid.to_string())
            .status()
            .map(|s| s.success())
            .unwrap_or(false)
    }
    
    #[cfg(not(unix))]
    {
        // Windows fallback: assume alive (will be removed when process exits)
        true
    }
}
