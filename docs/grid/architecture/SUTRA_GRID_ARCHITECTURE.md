# Sutra Grid Architecture
## Distributed Grid Computing for Scalable AI Reasoning

---

## Vision

**Problem:** Current Sutra deployment requires manual management of storage-server instances.  
**Solution:** A grid computing architecture where a master orchestrates agents that deploy compute anywhere.

**Goals:**
- Deploy storage-server to any platform (Docker, K8s, AWS, Azure, GCP, bare metal, desktop)
- Scale dynamically based on load
- Zero-touch deployment (master pushes binaries to agents)
- Platform-agnostic (agents adapt to local environment)
- Self-healing (auto-restart failed nodes)

---

## Architecture

```
                    ┌────────────────────────────────────────┐
                    │      SUTRA MASTER (Control Plane)      │
                    │  - Grid Orchestrator                   │
                    │  - Resource Manager                    │
                    │  - Deployment Engine                   │
                    │  - Health Monitor                      │
                    │  - Web UI (sutra-control)              │
                    └──────────────┬─────────────────────────┘
                                   │ gRPC Control Protocol
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
    ┌──────────┐             ┌──────────┐            ┌──────────┐
    │ AGENT    │             │ AGENT    │            │ AGENT    │
    │ (Docker) │             │ (K8s)    │            │ (AWS EC2)│
    └────┬─────┘             └────┬─────┘            └────┬─────┘
         │spawns                  │spawns                 │spawns
         ▼                        ▼                        ▼
    [storage-server]        [storage-server]        [storage-server]
    [storage-server]        [storage-server]        [storage-server]
         ...                     ...                      ...
```

---

## Components

### 1. Master (Control Plane)

**Location:** Runs as part of `sutra-control`

**Responsibilities:**
- **Discovery:** Agents register with master on startup
- **Scheduling:** Decides which agent should run which workload
- **Deployment:** Pushes storage-server binary to agents
- **Scaling:** Adds/removes nodes based on load
- **Health:** Monitors all nodes, restarts failed ones
- **Orchestration:** Coordinates leader election, replica placement

**API (gRPC Service):**
```protobuf
service GridMaster {
  // Agent lifecycle
  rpc RegisterAgent(AgentInfo) returns (AgentRegistration);
  rpc Heartbeat(AgentHeartbeat) returns (MasterCommand);
  rpc UnregisterAgent(AgentId) returns (Empty);
  
  // Node management
  rpc DeployNode(DeploymentRequest) returns (DeploymentResponse);
  rpc ScaleCluster(ScaleRequest) returns (ScaleResponse);
  rpc GetClusterStatus(Empty) returns (ClusterStatus);
  
  // Manual control
  rpc StartNode(NodeId) returns (OperationResult);
  rpc StopNode(NodeId) returns (OperationResult);
  rpc RestartNode(NodeId) returns (OperationResult);
}
```

**State:**
- Agent registry (IP, platform, capacity, health)
- Node registry (which agent runs which node)
- Cluster topology (leader, replicas)
- Deployment history

---

### 2. Agent (Deployed to Targets)

**Platforms:**
- Docker (via Docker API)
- Kubernetes (via kubectl/API)
- AWS (via boto3)
- Azure (via Azure SDK)
- GCP (via gcloud SDK)
- Bare metal (via systemd)
- Desktop (via process spawning)

**Responsibilities:**
- Register with master
- Download storage-server binary from master
- Spawn storage-server processes based on master commands
- Monitor local processes
- Report metrics to master
- Execute lifecycle commands (start/stop/restart)

**Implementation (Rust for portability):**
```rust
// sutra-agent binary (~5MB)
pub struct SutraAgent {
    master_addr: String,
    platform: Platform,  // Docker, K8s, SystemD, Process
    spawned_nodes: Vec<SpawnedNode>,
}

impl SutraAgent {
    pub async fn register(&self) -> Result<()> {
        // Connect to master, send platform info
    }
    
    pub async fn heartbeat_loop(&self) {
        // Every 5 seconds, send status to master
    }
    
    pub async fn spawn_storage_node(&mut self, config: NodeConfig) -> Result<()> {
        match self.platform {
            Platform::Docker => self.spawn_docker(config),
            Platform::Kubernetes => self.spawn_k8s(config),
            Platform::SystemD => self.spawn_systemd(config),
            Platform::Process => self.spawn_process(config),
        }
    }
    
    pub async fn kill_storage_node(&mut self, node_id: &str) -> Result<()> {
        // Stop node based on platform
    }
}
```

---

### 3. Storage Node (Compute Workers)

**Binary:** `storage-server` (~20MB)

**Grid-Aware:**
- Knows master address (from agent)
- Registers on startup
- Accepts control commands (shutdown, role change)

**No changes needed!** Existing storage-server works with minimal additions:
```rust
// Add to storage_server.rs main()
let master_addr = env::var("SUTRA_MASTER").ok();
if let Some(addr) = master_addr {
    register_with_master(&addr, node_id).await?;
}
```

---

## Deployment Scenarios

### Scenario 1: Hybrid Cloud (Docker + AWS)

```yaml
# Master configuration
master:
  agents:
    - name: "docker-local"
      platform: docker
      address: "localhost"
      capacity: 4  # Can run 4 storage nodes
      
    - name: "aws-east"
      platform: aws_ec2
      address: "agent.aws-east.example.com:50060"
      capacity: 10  # Can run 10 storage nodes
```

**Flow:**
1. User clicks "Scale to 10 nodes" in Web UI
2. Master checks available capacity:
   - docker-local: 4 available
   - aws-east: 10 available
3. Master sends deployment commands:
   - 4 nodes → docker-local agent
   - 6 nodes → aws-east agent
4. Agents spawn storage-server processes
5. Storage nodes register with master
6. Master configures replication topology

---

### Scenario 2: Pure Kubernetes

```yaml
# Master configuration
master:
  agents:
    - name: "k8s-production"
      platform: kubernetes
      namespace: "sutra-grid"
      kubeconfig: "/path/to/kubeconfig"
      capacity: 100  # Elastic scaling
```

**Agent creates Kubernetes Deployments:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sutra-storage-node-1
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: storage-server
        image: sutra-storage-server:v2
        env:
        - name: SUTRA_MASTER
          value: "master.sutra-grid.svc.cluster.local:50050"
```

---

### Scenario 3: Desktop Dev Environment

```yaml
# Master configuration
master:
  agents:
    - name: "macbook-local"
      platform: process
      address: "localhost"
      capacity: 2
```

**Agent spawns processes directly:**
```bash
# Agent runs:
./storage-server \
  --storage-path=/tmp/node1 \
  --port=50051 \
  --master=localhost:50050 &
  
./storage-server \
  --storage-path=/tmp/node2 \
  --port=50052 \
  --master=localhost:50050 &
```

---

## API Examples

### Deploy a 3-Node Cluster

```bash
# Via Web UI or API
curl -X POST http://localhost:9000/api/grid/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": 3,
    "topology": "leader-replicas",
    "placement": "auto"
  }'

# Master response:
{
  "deployment_id": "deploy-abc123",
  "nodes": [
    {"id": "node-1", "role": "leader", "agent": "docker-local", "port": 50051},
    {"id": "node-2", "role": "replica", "agent": "docker-local", "port": 50052},
    {"id": "node-3", "role": "replica", "agent": "aws-east", "port": 50051}
  ],
  "status": "provisioning"
}
```

### Scale Cluster

```bash
curl -X POST http://localhost:9000/api/grid/scale \
  -d '{"target_nodes": 10}'

# Master automatically:
# 1. Finds agents with capacity
# 2. Deploys 7 more nodes
# 3. Configures replication
```

### Manual Node Control

```bash
# Restart specific node
curl -X POST http://localhost:9000/api/grid/nodes/node-2/restart

# Promote replica to leader (failover)
curl -X POST http://localhost:9000/api/grid/nodes/node-2/promote
```

---

## Agent Installation

### Quick Install (any platform)

```bash
# Download agent binary
curl -LO https://github.com/sutra/releases/latest/sutra-agent

# Make executable
chmod +x sutra-agent

# Run (connects to master)
./sutra-agent \
  --master=master.example.com:50050 \
  --platform=docker \
  --capacity=4
```

### Kubernetes DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: sutra-agent
spec:
  template:
    spec:
      containers:
      - name: agent
        image: sutra-agent:v1
        env:
        - name: SUTRA_MASTER
          value: "master:50050"
        - name: SUTRA_PLATFORM
          value: "kubernetes"
```

---

## Implementation Phases

### Phase 1: Core Grid (2 weeks)
- [ ] gRPC proto definitions
- [ ] Master service in sutra-control
- [ ] Agent binary (Rust)
- [ ] Docker platform adapter
- [ ] Process platform adapter
- [ ] Web UI for grid management

**Deliverable:** Deploy 3-node cluster locally

---

### Phase 2: Multi-Platform (1 week)
- [ ] Kubernetes adapter
- [ ] SystemD adapter
- [ ] Cloud adapters (AWS, Azure, GCP)

**Deliverable:** Deploy across platforms

---

### Phase 3: Auto-Scaling (1 week)
- [ ] Load metrics collection
- [ ] Scaling policies (CPU, memory, request rate)
- [ ] Auto scale-up/scale-down
- [ ] Cost optimization

**Deliverable:** Auto-scale based on load

---

### Phase 4: Production Features (2 weeks)
- [ ] Binary distribution (master serves binaries)
- [ ] Rolling upgrades
- [ ] Blue-green deployments
- [ ] Disaster recovery
- [ ] Multi-region support

**Deliverable:** Production-ready grid

---

## File Structure

```
sutra-models/
├── packages/
│   ├── sutra-control/          # Master lives here
│   │   ├── backend/
│   │   │   ├── main.py         # Existing FastAPI app
│   │   │   └── grid/           # NEW: Grid orchestrator
│   │   │       ├── master.py
│   │   │       ├── scheduler.py
│   │   │       └── deployer.py
│   │   └── frontend/
│   │       └── src/
│   │           └── components/
│   │               └── GridDashboard.tsx  # NEW
│   │
│   ├── sutra-agent/            # NEW: Agent binary
│   │   ├── Cargo.toml
│   │   └── src/
│   │       ├── main.rs
│   │       ├── platforms/
│   │       │   ├── docker.rs
│   │       │   ├── kubernetes.rs
│   │       │   ├── systemd.rs
│   │       │   └── process.rs
│   │       └── master_client.rs
│   │
│   └── sutra-storage/          # Minor changes
│       └── src/
│           └── bin/
│               └── storage_server.rs  # Add master registration
│
└── proto/
    └── grid.proto              # NEW: Grid control protocol
```

---

## Comparison with Existing Solutions

| Feature | Sutra Grid | Kubernetes | Apache Mesos | Nomad |
|---------|-----------|------------|--------------|-------|
| **Purpose-built for Sutra** | ✅ | ❌ | ❌ | ❌ |
| **20MB binary deployment** | ✅ | ❌ (large) | ❌ (large) | ✅ |
| **Reasoning-aware scheduling** | ✅ | ❌ | ❌ | ❌ |
| **Zero external dependencies** | ✅ | ❌ (etcd, etc) | ❌ (ZK) | ✅ |
| **Multi-platform agents** | ✅ | K8s only | Limited | ✅ |
| **Desktop support** | ✅ | ❌ | ❌ | ❌ |

---

## Benefits

### For Users
- **One-click scaling:** "Scale to 10 nodes" button
- **Hybrid deployment:** Mix cloud + on-prem seamlessly
- **Cost optimization:** Deploy cheap nodes for read replicas, expensive for leader
- **Developer friendly:** Run full cluster on laptop

### For Sutra
- **Competitive advantage:** No one else has reasoning-aware grid
- **Ecosystem play:** Agents become distribution channel
- **Enterprise ready:** Multi-cloud, auto-scaling, self-healing

---

## Next Steps

**This week:**
1. Review this architecture
2. Decide on priorities (Docker-first vs multi-platform)
3. Create proto definitions

**Next 2 weeks:**
1. Implement Phase 1 (Core Grid)
2. Test 3-node local deployment
3. Integrate with existing sutra-control UI

**Month 2:**
1. Multi-platform support
2. Auto-scaling
3. Production hardening

---

## Open Questions

1. **Binary distribution:** Master serves binaries or agents download from GitHub?
   - **Recommendation:** Master serves (air-gapped deployments)

2. **Security:** How to authenticate agents?
   - **Recommendation:** JWT tokens issued by master

3. **Multi-region:** How to handle cross-region master-agent communication?
   - **Recommendation:** Regional masters with global coordinator

4. **Pricing model:** Grid as a service?
   - **Recommendation:** Free for self-hosted, premium for managed grid

---

## References

- Apache Mesos: https://mesos.apache.org/
- Nomad: https://www.nomadproject.io/
- Ray (ML grid): https://www.ray.io/
- BOINC (public grid): https://boinc.berkeley.edu/
