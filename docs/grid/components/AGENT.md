# Sutra Grid Agent

**Worker node for Sutra Grid** - registers with Master, sends heartbeats, and spawns storage nodes on command.

## Features

✅ **Master Connection**: Connects to Master via gRPC  
✅ **Auto-Registration**: Registers on startup with agent info  
✅ **Heartbeat Loop**: Sends heartbeats every 5 seconds  
✅ **Auto-Reconnect**: Reconnects and re-registers if Master connection lost  
✅ **Config File**: TOML-based configuration  
✅ **Storage Node Spawning**: Spawns storage node processes on command (Week 3)  
✅ **Process Monitoring**: Tracks spawned process PIDs (Week 3)  
✅ **Auto-Restart**: Restarts crashed storage nodes automatically (Week 3)

## Building

```bash
cd packages/sutra-grid-agent
cargo build --release
```

## Configuration

Edit `agent-config.toml`:

```toml
[agent]
agent_id = "agent-1"
master_host = "localhost:7000"
platform = "desktop"
max_storage_nodes = 10

[storage]
binary_path = "./target/release/storage-server"
data_path = "./data"
default_memory_mb = 2048
default_port_range_start = 50051

[monitoring]
heartbeat_interval_secs = 5
health_check_interval_secs = 10
restart_failed_nodes = true
```

## Running

### Prerequisites

1. Start Master first:
   ```bash
   cd packages/sutra-grid-master
   cargo run
   ```

2. Start Agent:
   ```bash
   cd packages/sutra-grid-agent
   cargo run
   ```

### With Custom Config

```bash
cargo run -- /path/to/custom-config.toml
```

## Expected Output

```
🚀 Sutra Grid Agent v0.1.0 starting...
📄 Loading config from agent-config.toml
⚙️  Config: Agent ID: agent-1, Platform: desktop, Max Nodes: 10
🔌 Connecting to Master at localhost:7000
✅ Connected to Master
📝 Registering with Master...
✅ Registered with Master (Master v0.1.0, Agent: agent-1, Host: your-hostname)
💓 Starting heartbeat loop (interval: 5s)
💓 Heartbeat #12 acknowledged (Master time: 1729218000)
💓 Heartbeat #24 acknowledged (Master time: 1729218060)
```

## Testing End-to-End

### Terminal 1: Start Master

```bash
cd packages/sutra-grid-master
RUST_LOG=info cargo run
```

**Expected:**
```
🚀 Sutra Grid Master v0.1.0 starting on 0.0.0.0:7000
📡 Listening for agent connections...
📊 Cluster: 0 agents (0 healthy), 0 storage nodes (0 running) - healthy
```

### Terminal 2: Start Agent

```bash
cd packages/sutra-grid-agent
RUST_LOG=info cargo run
```

**Expected:**
```
🚀 Sutra Grid Agent v0.1.0 starting...
✅ Registered with Master (Master v0.1.0, Agent: agent-1, Host: ...)
💓 Starting heartbeat loop (interval: 5s)
```

### Terminal 1: Master Logs

You should see:
```
📝 Agent registration request: agent-1 (desktop)
✅ Agent registered: agent-1 (total agents: 1)
💓 Heartbeat from agent-1 (nodes: 0)
📊 Cluster: 1 agents (1 healthy), 0 storage nodes (0 running) - healthy
```

## Auto-Reconnection

If Master crashes and restarts, Agent will:
1. Detect heartbeat failure
2. Wait 5 seconds
3. Reconnect to Master
4. Re-register automatically

Test it:
1. Stop Master (Ctrl+C)
2. Agent logs: `❌ Heartbeat failed` and `⚠️  Connection to Master lost`
3. Restart Master
4. Agent logs: `✅ Reconnected to Master` and `✅ Registered with Master`

## Logging

**Log levels:**
- `INFO`: Registration, heartbeats (every minute), connection status
- `DEBUG`: Every heartbeat
- `WARN`: Connection lost
- `ERROR`: Failed operations

**Set log level:**
```bash
RUST_LOG=debug cargo run
```

## Architecture

```
Agent
├── Config (TOML file)
│   ├── agent_id, master_host, platform
│   └── monitoring intervals
│
├── gRPC Client
│   ├── Connect to Master
│   ├── RegisterAgent()
│   └── Heartbeat()
│
└── Heartbeat Loop (background task)
    ├── Send heartbeat every 5s
    ├── Reconnect on failure
    └── Log every 12th heartbeat (1 minute)
```

## Next Steps

- [x] Connect to Master
- [x] Registration
- [x] Heartbeat loop
- [x] Auto-reconnection
- [x] Spawn storage nodes (Week 3) ✅
- [x] Monitor storage processes (Week 3) ✅
- [x] Auto-restart crashed nodes (Week 3) ✅
- [ ] Handle spawn requests from Master (Week 4)
- [ ] Real storage-server integration (Week 4)

## Related Documentation

- [Phase 1 Plan](../../../docs/sutra-storage/architecture/grid/PHASE1_MASTER_AGENT.md)
- [Grid Master](../sutra-grid-master/README.md)
