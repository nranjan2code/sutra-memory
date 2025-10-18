# Phase 1: Master + Agent Foundation

## Goal

Build the **control plane foundation** for Sutra Grid:
- **Master**: Control plane that discovers and manages agents
- **Agent**: Independent worker that spawns storage nodes
- **Protocol**: gRPC communication between Master and Agents

**No sharding, no replication yet** - just solid infrastructure for agent lifecycle management.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SUTRA MASTER (Control Plane)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │
│  │   Web UI     │  │ Cluster API  │  │   Grid Orchestrator      │ │
│  │   (React)    │  │  (FastAPI)   │  │ - Node Registry          │ │
│  │              │  │              │  │ - Deployment Engine       │ │
│  │              │  │              │  │ - Health Monitor          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘ │
└────────────┬────────────────────────────────────────────────────────┘
             │ gRPC Control Protocol
             │
    ┌────────┴────────┬────────────────┬──────────────┬─────────────┐
    │                 │                │              │             │
    ▼                 ▼                ▼              ▼             ▼
┌─────────┐     ┌─────────┐     ┌─────────┐    ┌─────────┐   ┌─────────┐
│ AGENT 1 │     │ AGENT 2 │     │ AGENT 3 │    │ AGENT 4 │   │ AGENT N │
│ (Docker)│     │  (K8s)  │     │ (AWS)   │    │(Desktop)│   │ (Azure) │
└────┬────┘     └────┬────┘     └────┬────┘    └────┬────┘   └────┬────┘
     │               │               │              │             │
     ├──spawns──►    ├──spawns──►    ├──spawns──►   ├──spawns──►  │
     ▼               ▼               ▼              ▼             ▼
[Storage]       [Storage]       [Storage]      [Storage]     [Storage]
[20MB bin]      [20MB bin]      [20MB bin]     [20MB bin]    [20MB bin]
[WAL+Data]      [WAL+Data]      [WAL+Data]     [WAL+Data]    [WAL+Data]
```

---

## Component Design

### 1. Master (Control Plane)

**Location:** `packages/sutra-grid-master/`

**Responsibilities:**
- Accept agent registrations
- Maintain agent registry (id, host, platform, capacity, status)
- Monitor agent health via heartbeats
- Provide deployment API (spawn/stop storage nodes)
- Expose REST API for UI/CLI

**Technology Stack:**
- **gRPC Server**: Agent communication (Rust + Tonic)
- **REST API**: UI/CLI access (Axum or Actix-web)
- **State Store**: In-memory (HashMap) + optional SQLite persistence

**API Surface:**

```protobuf
// grid.proto
service GridMaster {
    // Agent lifecycle
    rpc RegisterAgent(AgentInfo) returns (RegistrationResponse);
    rpc Heartbeat(HeartbeatRequest) returns (HeartbeatResponse);
    rpc UnregisterAgent(AgentId) returns (Empty);
    
    // Deployment control
    rpc SpawnStorageNode(SpawnRequest) returns (SpawnResponse);
    rpc StopStorageNode(StopRequest) returns (StopResponse);
    rpc GetStorageNodeStatus(NodeId) returns (NodeStatus);
    
    // Cluster info
    rpc ListAgents(Empty) returns (AgentList);
    rpc GetClusterStatus(Empty) returns (ClusterStatus);
}

message AgentInfo {
    string agent_id = 1;
    string hostname = 2;
    string platform = 3;  // "docker", "k8s", "aws", "desktop"
    uint32 max_storage_nodes = 4;
    string version = 5;
}

message SpawnRequest {
    string agent_id = 1;
    string storage_path = 2;
    uint64 memory_limit_mb = 3;
    uint32 port = 4;
}

message SpawnResponse {
    string node_id = 1;
    string endpoint = 2;  // host:port
    bool success = 3;
    string error_message = 4;
}
```

**Rust Implementation Skeleton:**

```rust
// packages/sutra-grid-master/src/main.rs
use tonic::{transport::Server, Request, Response, Status};
use std::sync::Arc;
use tokio::sync::RwLock;
use std::collections::HashMap;

mod grid {
    tonic::include_proto!("grid");
}

struct AgentRecord {
    id: String,
    hostname: String,
    platform: String,
    max_nodes: u32,
    last_heartbeat: u64,
    status: AgentStatus,
    storage_nodes: Vec<StorageNodeInfo>,
}

struct StorageNodeInfo {
    node_id: String,
    endpoint: String,
    pid: Option<u32>,
    status: NodeStatus,
}

enum AgentStatus {
    Healthy,
    Degraded,
    Offline,
}

enum NodeStatus {
    Starting,
    Running,
    Stopping,
    Stopped,
    Failed,
}

struct GridMasterService {
    agents: Arc<RwLock<HashMap<String, AgentRecord>>>,
}

#[tonic::async_trait]
impl grid::grid_master_server::GridMaster for GridMasterService {
    async fn register_agent(
        &self,
        request: Request<grid::AgentInfo>,
    ) -> Result<Response<grid::RegistrationResponse>, Status> {
        let info = request.into_inner();
        
        let mut agents = self.agents.write().await;
        agents.insert(info.agent_id.clone(), AgentRecord {
            id: info.agent_id.clone(),
            hostname: info.hostname,
            platform: info.platform,
            max_nodes: info.max_storage_nodes,
            last_heartbeat: current_timestamp(),
            status: AgentStatus::Healthy,
            storage_nodes: Vec::new(),
        });
        
        log::info!("✅ Agent registered: {}", info.agent_id);
        
        Ok(Response::new(grid::RegistrationResponse {
            success: true,
            master_version: env!("CARGO_PKG_VERSION").to_string(),
        }))
    }
    
    async fn heartbeat(
        &self,
        request: Request<grid::HeartbeatRequest>,
    ) -> Result<Response<grid::HeartbeatResponse>, Status> {
        let req = request.into_inner();
        
        let mut agents = self.agents.write().await;
        if let Some(agent) = agents.get_mut(&req.agent_id) {
            agent.last_heartbeat = current_timestamp();
            agent.status = AgentStatus::Healthy;
        }
        
        Ok(Response::new(grid::HeartbeatResponse {
            acknowledged: true,
            timestamp: current_timestamp(),
        }))
    }
    
    async fn spawn_storage_node(
        &self,
        request: Request<grid::SpawnRequest>,
    ) -> Result<Response<grid::SpawnResponse>, Status> {
        let req = request.into_inner();
        
        // Forward spawn request to agent via separate gRPC client
        // Agent will actually spawn the process and report back
        
        // For now, just track the request
        log::info!("📦 Spawn request for agent {}", req.agent_id);
        
        Ok(Response::new(grid::SpawnResponse {
            node_id: format!("node-{}", uuid::Uuid::new_v4()),
            endpoint: format!("{}:50051", "localhost"),
            success: true,
            error_message: String::new(),
        }))
    }
    
    // ... other methods
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    let service = GridMasterService {
        agents: Arc::new(RwLock::new(HashMap::new())),
    };
    
    let addr = "0.0.0.0:7000".parse()?;
    
    log::info!("🚀 Sutra Grid Master starting on {}", addr);
    
    Server::builder()
        .add_service(grid::grid_master_server::GridMasterServer::new(service))
        .serve(addr)
        .await?;
    
    Ok(())
}

fn current_timestamp() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
}
```

---

### 2. Agent (Worker Node)

**Location:** `packages/sutra-grid-agent/`

**Responsibilities:**
- Register with Master on startup
- Send heartbeats every 5 seconds
- Spawn storage node processes on command
- Monitor spawned processes (restart on crash)
- Report node status to Master

**Platform Support:**
- **Docker**: Spawn storage containers
- **Desktop**: Spawn storage processes directly
- **K8s**: Create storage pods
- **AWS/Azure**: Launch EC2/VM instances (future)

**Technology Stack:**
- **gRPC Client**: Talk to Master (Rust + Tonic)
- **Process Manager**: Spawn and monitor storage nodes (tokio::process)
- **Config**: TOML file for agent settings

**Agent Configuration:**

```toml
# agent-config.toml
[agent]
agent_id = "agent-1"
master_host = "master.sutra.internal:7000"
platform = "docker"  # "docker", "desktop", "k8s"
max_storage_nodes = 10

[storage]
binary_path = "/usr/local/bin/storage-server"
data_path = "/data/sutra"
default_memory_mb = 2048
default_port_range = "50051-50060"

[monitoring]
heartbeat_interval_secs = 5
health_check_interval_secs = 10
restart_failed_nodes = true
```

**Rust Implementation Skeleton:**

```rust
// packages/sutra-grid-agent/src/main.rs
use tonic::transport::Channel;
use tokio::process::Command;
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;

mod grid {
    tonic::include_proto!("grid");
}

struct AgentConfig {
    agent_id: String,
    master_host: String,
    platform: String,
    max_nodes: u32,
    binary_path: String,
    data_path: String,
}

struct StorageProcess {
    node_id: String,
    pid: u32,
    port: u32,
    handle: tokio::task::JoinHandle<()>,
}

struct Agent {
    config: AgentConfig,
    master_client: grid::grid_master_client::GridMasterClient<Channel>,
    storage_processes: Arc<RwLock<HashMap<String, StorageProcess>>>,
}

impl Agent {
    async fn new(config: AgentConfig) -> Result<Self, Box<dyn std::error::Error>> {
        let master_client = grid::grid_master_client::GridMasterClient::connect(
            format!("http://{}", config.master_host)
        ).await?;
        
        Ok(Self {
            config,
            master_client,
            storage_processes: Arc::new(RwLock::new(HashMap::new())),
        })
    }
    
    async fn register(&mut self) -> Result<(), Box<dyn std::error::Error>> {
        let request = grid::AgentInfo {
            agent_id: self.config.agent_id.clone(),
            hostname: hostname::get()?.to_string_lossy().to_string(),
            platform: self.config.platform.clone(),
            max_storage_nodes: self.config.max_nodes,
            version: env!("CARGO_PKG_VERSION").to_string(),
        };
        
        let response = self.master_client.register_agent(request).await?;
        
        if response.into_inner().success {
            log::info!("✅ Registered with Master");
        }
        
        Ok(())
    }
    
    async fn heartbeat_loop(&mut self) {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(5));
        
        loop {
            interval.tick().await;
            
            let request = grid::HeartbeatRequest {
                agent_id: self.config.agent_id.clone(),
                storage_node_count: self.storage_processes.read().await.len() as u32,
                timestamp: current_timestamp(),
            };
            
            match self.master_client.heartbeat(request).await {
                Ok(_) => log::debug!("💓 Heartbeat sent"),
                Err(e) => log::error!("❌ Heartbeat failed: {}", e),
            }
        }
    }
    
    async fn spawn_storage_node(
        &self,
        node_id: String,
        port: u32,
        storage_path: String,
    ) -> Result<u32, Box<dyn std::error::Error>> {
        log::info!("📦 Spawning storage node: {}", node_id);
        
        let mut cmd = Command::new(&self.config.binary_path);
        cmd.arg("--port").arg(port.to_string())
           .arg("--storage-path").arg(&storage_path)
           .arg("--node-id").arg(&node_id);
        
        let child = cmd.spawn()?;
        let pid = child.id().ok_or("Failed to get PID")?;
        
        // Monitor process
        let handle = tokio::spawn(async move {
            let status = child.wait_with_output().await;
            match status {
                Ok(output) => {
                    log::info!("Storage node {} exited: {:?}", node_id, output.status);
                }
                Err(e) => {
                    log::error!("Storage node {} error: {}", node_id, e);
                }
            }
        });
        
        let process = StorageProcess {
            node_id: node_id.clone(),
            pid,
            port,
            handle,
        };
        
        self.storage_processes.write().await.insert(node_id, process);
        
        Ok(pid)
    }
    
    async fn monitor_storage_nodes(&self) {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(10));
        
        loop {
            interval.tick().await;
            
            let processes = self.storage_processes.read().await;
            for (node_id, process) in processes.iter() {
                // Check if process is still alive
                if process.handle.is_finished() {
                    log::warn!("⚠️ Storage node {} crashed, restarting...", node_id);
                    // TODO: Restart logic
                }
            }
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    env_logger::init();
    
    let config = AgentConfig {
        agent_id: "agent-1".to_string(),
        master_host: "localhost:7000".to_string(),
        platform: "desktop".to_string(),
        max_nodes: 10,
        binary_path: "./target/release/storage-server".to_string(),
        data_path: "./data".to_string(),
    };
    
    let mut agent = Agent::new(config).await?;
    
    // Register with Master
    agent.register().await?;
    
    // Start background tasks
    let heartbeat_handle = tokio::spawn(async move {
        agent.heartbeat_loop().await;
    });
    
    heartbeat_handle.await?;
    
    Ok(())
}

fn current_timestamp() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_secs()
}
```

---

### 3. Storage Node Binary (20MB)

**Location:** `packages/sutra-storage/` (already exists!)

**Modifications Needed:**
- Add CLI args: `--port`, `--storage-path`, `--node-id`
- Add gRPC server for Master queries
- Keep existing WAL + ConcurrentStorage

**Minimal Changes:**

```rust
// packages/sutra-storage/src/bin/storage-server.rs
use clap::Parser;
use sutra_storage::ConcurrentMemory;

#[derive(Parser)]
struct Args {
    #[arg(long, default_value = "50051")]
    port: u16,
    
    #[arg(long, default_value = "./storage")]
    storage_path: String,
    
    #[arg(long)]
    node_id: String,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    
    log::info!("🚀 Storage Node {} starting on port {}", args.node_id, args.port);
    
    // Initialize storage
    let config = sutra_storage::ConcurrentConfig {
        storage_path: args.storage_path.into(),
        ..Default::default()
    };
    
    let storage = ConcurrentMemory::new(config);
    
    // Start gRPC server (existing storage-server gRPC code)
    // ...
    
    Ok(())
}
```

---

## Implementation Plan

### Week 1: Master Foundation
- [ ] Create `packages/sutra-grid-master/` Rust project
- [ ] Define `grid.proto` with basic RPCs
- [ ] Implement `RegisterAgent` and `Heartbeat` handlers
- [ ] Add in-memory agent registry (HashMap)
- [ ] Basic REST API (GET /agents, GET /status)
- [ ] Unit tests for registration and heartbeat

**Deliverable:** Master can accept agent registrations and track heartbeats

---

### Week 2: Agent Foundation
- [ ] Create `packages/sutra-grid-agent/` Rust project
- [ ] Implement gRPC client to Master
- [ ] Agent registration on startup
- [ ] Heartbeat loop (every 5 seconds)
- [ ] Load agent config from TOML file
- [ ] Unit tests for registration and heartbeat

**Deliverable:** Agent can register and maintain connection to Master

---

### Week 3: Storage Node Spawning
- [ ] Add `SpawnStorageNode` RPC to Master
- [ ] Implement process spawning in Agent (tokio::process)
- [ ] Agent monitors spawned processes (PID tracking)
- [ ] Auto-restart crashed processes
- [ ] Add `--port`, `--storage-path`, `--node-id` CLI args to storage-server
- [ ] Integration test: Master → Agent → Spawn storage node

**Deliverable:** Agent can spawn and monitor storage nodes on command

---

### Week 4: Integration & Testing
- [ ] End-to-end test: Master + 3 Agents + 9 Storage nodes
- [ ] Test agent crash recovery
- [ ] Test storage node crash recovery
- [ ] Basic CLI tool (`sutra-grid-cli`)
- [ ] Documentation: How to deploy Master + Agents
- [ ] Docker images for Master and Agent

**Deliverable:** Working grid with Master + Agents managing storage nodes

---

## Testing Strategy

### Unit Tests
```rust
// Master tests
#[tokio::test]
async fn test_agent_registration() {
    let master = GridMasterService::new();
    let request = AgentInfo { /* ... */ };
    let response = master.register_agent(Request::new(request)).await.unwrap();
    assert!(response.into_inner().success);
}

#[tokio::test]
async fn test_heartbeat_updates_timestamp() {
    let master = GridMasterService::new();
    // Register agent
    // Send heartbeat
    // Verify timestamp updated
}
```

### Integration Tests
```rust
// End-to-end test
#[tokio::test]
async fn test_spawn_storage_node_e2e() {
    // 1. Start Master
    let master = spawn_master().await;
    
    // 2. Start Agent
    let agent = spawn_agent(master.addr()).await;
    
    // 3. Spawn storage node
    let response = master.spawn_storage_node(/* ... */).await;
    
    // 4. Verify node is running
    assert!(response.success);
    assert!(agent.has_running_process(response.node_id));
}
```

---

## File Structure

```
sutra-models/
├── packages/
│   ├── sutra-grid-master/
│   │   ├── Cargo.toml
│   │   ├── proto/
│   │   │   └── grid.proto
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── registry.rs
│   │   │   ├── api.rs
│   │   │   └── grpc_service.rs
│   │   └── tests/
│   │       └── integration_tests.rs
│   │
│   ├── sutra-grid-agent/
│   │   ├── Cargo.toml
│   │   ├── agent-config.toml
│   │   ├── src/
│   │   │   ├── main.rs
│   │   │   ├── spawner.rs
│   │   │   ├── monitor.rs
│   │   │   └── grpc_client.rs
│   │   └── tests/
│   │       └── integration_tests.rs
│   │
│   └── sutra-storage/
│       ├── src/
│       │   └── bin/
│       │       └── storage-server.rs (modify for CLI args)
│       └── ... (existing code)
│
└── docs/
    └── sutra-storage/
        └── architecture/
            └── grid/
                └── PHASE1_MASTER_AGENT.md (this file)
```

---

## Success Criteria

Phase 1 is **DONE** when:

1. ✅ Master accepts agent registrations
2. ✅ Agents send heartbeats every 5 seconds
3. ✅ Master detects agent failures (missed heartbeats)
4. ✅ Agent spawns storage nodes on command
5. ✅ Agent monitors storage nodes and restarts on crash
6. ✅ End-to-end test: Master + 3 Agents + 9 Storage nodes runs for 1 hour without issues
7. ✅ Docker images for Master and Agent published
8. ✅ CLI tool to manage cluster (`sutra-grid-cli`)

---

## What's NOT in Phase 1

- ❌ Sharding (all storage nodes are independent, no data distribution)
- ❌ Replication (no WAL streaming between nodes)
- ❌ Query routing (no concept of "which node has which data")
- ❌ Auto-scaling (manual spawn only)
- ❌ Web UI (CLI only)
- ❌ Multi-platform agents (desktop only, Docker/K8s later)

**Phase 1 = Infrastructure only** - build the pipes, worry about water flow later.

---

## Next Steps After Phase 1

Once Master + Agent foundation is solid:
- **Phase 2**: Add Shard Map to Master, implement routing
- **Phase 3**: Add WAL streaming for replication
- **Phase 4**: Auto-scaling and rebalancing
- **Phase 5**: Web UI and advanced features

But **first**, let's get the foundation right. A solid control plane is the key to everything else.
