# Sutra Grid Architecture

**Status**: Production-Ready (Week 4 Complete + Event-Driven Observability)  
**Version**: 1.0  
**Last Updated**: 2025-10-18

## Overview

Sutra Grid is a distributed infrastructure for managing storage nodes across multiple agents. It provides production-grade orchestration with bidirectional gRPC communication, automatic failover, and event-driven observability.

**Key Innovation**: Grid monitors itself using Sutra's own knowledge graph - proving the platform works out-of-the-box without external LMT (Logs/Metrics/Telemetry) dependencies.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      Grid Master (Port 7000)                    │
│  • Agent registration & health monitoring                       │
│  • Storage node lifecycle orchestration                         │
│  • Cluster status aggregation                                  │
│  • Event emission (observability)                               │
│  • Agent gRPC client pool with caching                         │
└────────────┬───────────────────────────────────────────────────┘
             │ gRPC (Bidirectional)
             ├──────────────────┬──────────────────┬───────────
             │                  │                  │
             ▼                  ▼                  ▼
    ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
    │  Grid Agent 1  │ │  Grid Agent 2  │ │  Grid Agent N  │
    │  (Port 8001)   │ │  (Port 8002)   │ │  (Port 800N)   │
    │                │ │                │ │                │
    │  gRPC Server   │ │  gRPC Server   │ │  gRPC Server   │
    │  • SpawnNode   │ │  • SpawnNode   │ │  • SpawnNode   │
    │  • StopNode    │ │  • StopNode    │ │  • StopNode    │
    │  • GetStatus   │ │  • GetStatus   │ │  • GetStatus   │
    │  • ListNodes   │ │  • ListNodes   │ │  • ListNodes   │
    │  • Events      │ │  • Events      │ │  • Events      │
    └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
             │                  │                  │
             ▼                  ▼                  ▼
    Storage Nodes       Storage Nodes       Storage Nodes
    (Port 50051+)       (Port 50051+)       (Port 50051+)

                            ↓ All Events
              ┌─────────────────────────────────────┐
              │  Sutra Storage (Reserved: 50052)    │
              │  Event-Driven Observability         │
              └─────────────────────────────────────┘
                            ↓ Query
              ┌─────────────────────────────────────┐
              │     Sutra Control (Grid Pane)       │
              │  Natural Language Queries           │
              └─────────────────────────────────────┘
```

## Components

### 1. Grid Master (sutra-grid-master)
**Location**: `packages/sutra-grid-master`  
**Port**: 7000 (gRPC)  
**Language**: Rust

**Responsibilities**:
- Agent registration and lifecycle management
- Storage node orchestration (spawn, stop, status)
- Cluster health monitoring (heartbeats, degradation detection)
- Event emission for observability
- Load balancing and resource allocation (future)

**Key Features**:
- Exponential backoff retry (100ms → 200ms → 400ms)
- Request timeouts (30s spawn, 10s stop, 5s status)
- Agent client connection pooling with cache invalidation
- Automatic agent health detection (degraded at 15s, offline at 30s)
- Graceful degradation if event storage unavailable

**Events Emitted**:
- AgentRegistered, AgentDegraded, AgentOffline, AgentRecovered, AgentUnregistered
- SpawnRequested, SpawnSucceeded, SpawnFailed
- StopRequested, StopSucceeded, StopFailed

### 2. Grid Agent (sutra-grid-agent)
**Location**: `packages/sutra-grid-agent`  
**Port**: 8001 (default, configurable)  
**Language**: Rust

**Responsibilities**:
- Storage node process management (spawn, monitor, restart)
- gRPC server for Master commands
- Heartbeat transmission (every 5s)
- Crash detection and auto-recovery
- Event emission for node lifecycle

**Key Features**:
- Auto-restart crashed nodes (up to 3 times)
- Process monitoring every 10s
- PID tracking and lifecycle management
- Resource limits enforcement (memory, storage)
- Graceful degradation if event storage unavailable

**Events Emitted**:
- NodeCrashed (with exit code)
- NodeRestarted (with restart count and new PID)

### 3. Grid Events (sutra-grid-events)
**Location**: `packages/sutra-grid-events`  
**Language**: Rust

**Responsibilities**:
- Event type definitions (17 events)
- EventEmitter with async background worker
- gRPC client for Sutra Storage
- Event → Concept + Associations mapping

**Key Features**:
- Non-blocking emission (<0.1ms overhead)
- Unbounded channel for event queue
- Async background worker for storage writes
- Automatic association creation (entity→event, event→timestamp)
- Graceful connection handling

**Event Types** (17 total):
- **Agent Lifecycle** (6): Registered, Heartbeat, Degraded, Offline, Recovered, Unregistered
- **Node Lifecycle** (6): SpawnRequested/Succeeded/Failed, StopRequested/Succeeded/Failed
- **Node Health** (2): NodeCrashed, NodeRestarted
- **Cluster Health** (3): ClusterHealthy, ClusterDegraded, ClusterCritical

### 4. CLI Tool (sutra-grid-cli)
**Location**: `packages/sutra-grid-master/src/bin/cli.rs`  
**Language**: Rust

**Commands**:
- `list-agents` - Show all registered agents
- `status` - Cluster health overview
- `spawn` - Create storage node on specific agent
- `stop` - Stop storage node
- `node-status` - Query node details

**Usage**:
```bash
sutra-grid-cli --master http://localhost:7000 spawn \
  --agent agent-001 \
  --port 50051 \
  --storage-path /tmp/node1 \
  --memory 1024
```

### 5. Reserved Storage Instance
**Location**: `packages/sutra-storage`  
**Port**: 50052 (reserved for Grid events)  
**Language**: Rust

**Purpose**: Dedicated storage instance for Grid observability events.

**Bootstrap**: `./bootstrap-grid-events.sh`

**Data Structure**:
```
Concepts:
  event-{type}-{timestamp_micros}
  
Associations:
  agent-001 --[event_type_code]--> event-{id}
  node-abc  --[event_type_code]--> event-{id}
  event-{id} --[999 (temporal)]--> ts-{timestamp}
```

### 6. Control Center Grid Interface ✅
**Location**: `packages/sutra-control`  
**Port**: 9000 (HTTP/WebSocket)  
**Language**: React + FastAPI

**Responsibilities**:
- Web-based Grid management interface
- Real-time cluster monitoring and status display
- Interactive storage node operations (spawn/stop)
- REST API endpoints for Grid operations
- Integration with existing Sutra Control Center

**Key Features**:
- **Grid Dashboard**: Real-time metrics for agents and storage nodes
- **Agent Management**: Expandable list view with detailed agent information
- **Node Operations**: Point-and-click spawn/stop with configurable parameters
- **Auto-refresh**: Updates every 10 seconds for live monitoring
- **Error Handling**: Graceful degradation when Grid Master unavailable
- **API Integration**: Complete REST endpoints for programmatic access

**REST API Endpoints**:
- `GET /api/grid/agents` - List all registered agents
- `GET /api/grid/status` - Get cluster health status
- `GET /api/grid/events` - Query Grid events from Sutra Storage
- `POST /api/grid/spawn` - Spawn new storage node
- `POST /api/grid/stop` - Stop running storage node
- `POST /api/grid/query` - Natural language Grid queries (planned)

**Access**: http://localhost:9000/grid (Grid Management tab)

**Architecture Integration**:
- Communicates with Grid Master via gRPC (primary)
- Falls back to Sutra Storage for historical data (secondary)
- Uses mock data for development/testing (tertiary)

## Communication Protocols

### Master ↔ Agent (Bidirectional gRPC)

**Master → Agent** (grid.proto):
- `RegisterAgent(AgentInfo) → RegistrationResponse`
- `Heartbeat(HeartbeatRequest) → HeartbeatResponse`
- `UnregisterAgent(AgentId) → Empty`
- `SpawnStorageNode(SpawnRequest) → SpawnResponse`
- `StopStorageNode(StopRequest) → StopResponse`
- `GetStorageNodeStatus(NodeId) → NodeStatus`
- `ListAgents(Empty) → AgentList`
- `GetClusterStatus(Empty) → ClusterStatus`

**Agent → Master** (agent.proto):
- `SpawnNode(SpawnNodeRequest) → SpawnNodeResponse`
- `StopNode(StopNodeRequest) → StopNodeResponse`
- `GetNodeStatus(NodeStatusRequest) → NodeStatusResponse`
- `ListNodes(ListNodesRequest) → ListNodesResponse`

### Grid Components ↔ Storage (Event Emission)

**Storage Integration** (storage.proto):
- `LearnConcept(LearnConceptRequest) → LearnConceptResponse`
- `LearnAssociation(LearnAssociationRequest) → LearnAssociationResponse`
- `QueryConcept(QueryConceptRequest) → QueryConceptResponse`
- `GetNeighbors(GetNeighborsRequest) → GetNeighborsResponse`

Events written as concepts with typed associations for queryability.

## Production Features

### Reliability
- **Retry Logic**: 3 attempts with exponential backoff (100ms → 200ms → 400ms)
- **Timeouts**: 30s spawn, 10s stop, 5s status queries
- **Auto-Recovery**: Crashed nodes restart automatically (up to 3 times)
- **Health Monitoring**: Agents marked degraded (15s) → offline (30s)
- **Graceful Degradation**: System works without event storage

### Observability
- **Event-Driven**: 17 structured event types
- **Zero LMT**: No Prometheus/Grafana/ELK needed
- **Self-Hosted**: Sutra monitors Sutra
- **Queryable**: Events stored as graph concepts
- **Natural Language**: Query via chat (Sutra Control)

### Performance
- **Event Emission**: <0.1ms (non-blocking)
- **Storage Write**: ~1ms (async worker)
- **Query Latency**: <10ms (graph traversal)
- **Client Connection**: ~100ms (with caching: <10ms)
- **Spawn Operation**: 50-200ms (includes process spawn)
- **Stop Operation**: 10-50ms (graceful shutdown)

### Error Handling
- `NOT_FOUND`: Agent/node not registered
- `UNAVAILABLE`: Agent offline or unreachable
- `DEADLINE_EXCEEDED`: Operation timeout
- `INTERNAL`: Communication failure

All errors propagated with context, emitted as events, and logged.

## Deployment

### Development (Local)

```bash
# Terminal 1: Reserved Storage
cd packages/sutra-storage
./bootstrap-grid-events.sh

# Terminal 2: Master
cd packages/sutra-grid-master
EVENT_STORAGE=http://localhost:50052 cargo run --release

# Terminal 3: Agent
cd packages/sutra-grid-agent
EVENT_STORAGE=http://localhost:50052 cargo run --release

# Terminal 4: CLI
cd packages/sutra-grid-master
./target/release/sutra-grid-cli list-agents
```

### Production (Docker Compose)

```yaml
services:
  grid-events-storage:
    image: sutra-storage:latest
    ports:
      - "50052:50052"
    volumes:
      - grid-events:/data
      
  grid-master:
    image: sutra-grid-master:latest
    ports:
      - "7000:7000"
    environment:
      EVENT_STORAGE: http://grid-events-storage:50052
    depends_on:
      - grid-events-storage
      
  grid-agent-1:
    image: sutra-grid-agent:latest
    environment:
      EVENT_STORAGE: http://grid-events-storage:50052
      AGENT_ID: agent-001
      MASTER_ENDPOINT: http://grid-master:7000
    depends_on:
      - grid-master
```

## Configuration

### Master
No configuration file. Uses environment variables:
- `EVENT_STORAGE`: Event storage endpoint (default: http://localhost:50052)

### Agent (`agent-config.toml`)
```toml
[agent]
agent_id = "agent-001"
master_endpoint = "http://localhost:7000"
agent_port = 8001  # gRPC server port
platform = "linux-x86_64"
max_storage_nodes = 5

[storage]
binary_path = "../sutra-storage-server/storage-server.sh"
data_path = "/tmp/sutra-nodes"
default_memory_mb = 512
default_port_range_start = 50051

[monitoring]
heartbeat_interval_secs = 5
health_check_interval_secs = 10
restart_failed_nodes = true
```

## Testing

### Integration Tests
```bash
# Automated end-to-end test
cd packages/sutra-grid-master
./test-integration.sh

# Expected: All 5 tests pass
✅ Cluster status retrieved
✅ Agents listed
✅ Node spawned successfully
✅ Node status retrieved
✅ Node stopped successfully
```

### Manual Testing
See `../events/GRID_EVENTS_TESTING_GUIDE.md` for detailed scenarios:
- Normal operations
- Agent degradation & recovery
- Node crash & auto-restart
- Spawn failures
- Network partitions

## Implementation Timeline

### Week 1 (Completed) ✅
- Master gRPC server
- Agent registration & heartbeats
- Basic health monitoring

### Week 2 (Completed) ✅
- Agent gRPC server
- Storage node spawning
- Process monitoring

### Week 3 (Completed) ✅
- Agent process tracking
- Crash detection
- Auto-restart logic

### Week 4 (Completed) ✅
- Master → Agent bidirectional gRPC
- Retry logic with exponential backoff
- Timeouts for all operations
- Client connection pooling
- Real-time status queries
- CLI tool

### Event-Driven Observability (Completed) ✅
- sutra-grid-events package (17 events)
- EventEmitter with async worker
- Master event integration (11 events)
- Agent event integration (2 events)
- Reserved storage bootstrap
- Testing guide & documentation

## Future Enhancements

### Phase 2: Intelligent Operations
- Automatic load balancing across agents
- Predictive scaling based on event patterns
- Node migration between agents
- Resource optimization
- Cost analysis from event data

### Phase 3: Advanced Observability
- Semantic embeddings for events (better search)
- Real-time anomaly detection
- Trend analysis and forecasting
- Custom alerting rules
- SLA monitoring and reporting

### Phase 4: Sutra Control Integration
- Grid management dashboard (React)
- Event stream visualization
- Natural language query interface
- Agent/node topology view
- Interactive troubleshooting

## Key Innovations

1. **Self-Hosting**: Sutra monitors itself
2. **Zero LMT**: No external observability stack
3. **Out-of-the-Box**: No platform modifications
4. **Events as Concepts**: Queryable through knowledge graph
5. **Natural Language**: Chat-based operations
6. **Production-Grade**: Enterprise reliability features

## Documentation

- **GRID_ARCHITECTURE.md** (this file): Complete architecture
- **../operations/WEEK4_INTEGRATION.md**: Master-Agent gRPC integration
- **../operations/WEEK4_QUICKSTART.md**: 5-minute setup guide
- **../events/EVENT_INTEGRATION.md**: Event-driven observability philosophy
- **../events/EVENT_IMPLEMENTATION_SUMMARY.md**: Implementation details
- **../events/GRID_EVENTS_TESTING_GUIDE.md**: Comprehensive testing scenarios
- **../reports/FINAL_STATUS.md**: Current status and roadmap

## Performance Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Event Emission | <0.1ms | Non-blocking |
| Storage Write | ~1ms | Async worker |
| Agent Registration | ~50ms | One-time |
| Heartbeat | <1ms | Cached write |
| Spawn Node | 50-200ms | Includes process |
| Stop Node | 10-50ms | Graceful shutdown |
| Status Query (cached) | <1ms | In-memory |
| Status Query (real-time) | <5ms | gRPC roundtrip |
| Client Connection | ~100ms | TLS handshake |
| Retry Overhead | 700ms max | 3 attempts |

## Success Metrics

✅ **Master**: All 11 events emitted  
✅ **Agent**: Both node events emitted  
✅ **Storage**: Events written as concepts  
✅ **Reliability**: Auto-restart working  
✅ **Performance**: <1ms event emission  
✅ **Error Handling**: Graceful degradation  
✅ **Documentation**: Comprehensive guides  
✅ **Testing**: End-to-end verified  

**Overall Status**: Production-Ready ✅

---

**Sutra Grid proves that event-driven observability works** - structured events in a knowledge graph, queryable through natural language, with zero external dependencies.

**Applications should emit events, not logs.**
