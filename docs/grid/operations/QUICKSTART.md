# Sutra Grid Quick Start

Test the **Master + Agent** foundation in under 5 minutes.

## Prerequisites

- Rust installed (`cargo --version`)
- Two terminal windows

## Step 1: Build Everything

```bash
cd /Users/nisheethranjan/Projects/sutra-models

# Build Master
cd packages/sutra-grid-master && cargo build

# Build Agent
cd ../sutra-grid-agent && cargo build
```

## Step 2: Start Master

**Terminal 1:**
```bash
cd packages/sutra-grid-master
cargo run
```

**Expected output:**
```
🚀 Sutra Grid Master v0.1.0 starting on 0.0.0.0:7000
📡 Listening for agent connections...
📊 Cluster: 0 agents (0 healthy), 0 storage nodes (0 running) - healthy
```

✅ Master is ready!

## Step 3: Start Agent

**Terminal 2:**
```bash
cd packages/sutra-grid-agent
cargo run
```

**Expected output:**
```
🚀 Sutra Grid Agent v0.1.0 starting...
📄 Loading config from agent-config.toml
⚙️  Config: Agent ID: agent-1, Platform: desktop, Max Nodes: 10
🔌 Connecting to Master at localhost:7000
✅ Connected to Master
📝 Registering with Master...
✅ Registered with Master (Master v0.1.0, Agent: agent-1, Host: your-hostname)
💓 Starting heartbeat loop (interval: 5s)
```

## Step 4: Watch the Magic ✨

**Terminal 1 (Master) should now show:**
```
📝 Agent registration request: agent-1 (desktop)
✅ Agent registered: agent-1 (total agents: 1)
💓 Heartbeat from agent-1 (nodes: 0)
💓 Heartbeat from agent-1 (nodes: 0)
📊 Cluster: 1 agents (1 healthy), 0 storage nodes (0 running) - healthy
```

**Terminal 2 (Agent) continues:**
```
💓 Heartbeat #12 acknowledged (Master time: ...)
💓 Heartbeat #24 acknowledged (Master time: ...)
```

✅ **SUCCESS!** Agent is registered and sending heartbeats.

---

## Test Reconnection

### Kill Master (Terminal 1)
Press `Ctrl+C` in Terminal 1

**Agent (Terminal 2) logs:**
```
❌ Heartbeat failed: ...
⚠️  Connection to Master lost, will retry...
❌ Reconnection failed: ...
```

### Restart Master (Terminal 1)
```bash
cargo run
```

**Agent auto-recovers:**
```
✅ Reconnected to Master
📝 Registering with Master...
✅ Registered with Master (Master v0.1.0, Agent: agent-1, Host: ...)
💓 Heartbeat #N acknowledged
```

✅ **Resilient!** Agent auto-reconnects and re-registers.

---

## Test Multiple Agents

### Agent 2 Config

Create `agent-config-2.toml`:
```toml
[agent]
agent_id = "agent-2"
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

### Start Second Agent

**Terminal 3:**
```bash
cd packages/sutra-grid-agent
cargo run -- agent-config-2.toml
```

**Master now shows:**
```
📝 Agent registration request: agent-2 (desktop)
✅ Agent registered: agent-2 (total agents: 2)
💓 Heartbeat from agent-2 (nodes: 0)
📊 Cluster: 2 agents (2 healthy), 0 storage nodes (0 running) - healthy
```

✅ **Multi-Agent Grid!** 

---

## Verify Health Monitoring

### Stop Agent 1 (Terminal 2)
Press `Ctrl+C`

**Wait 15 seconds...**

**Master logs:**
```
⚠️  Agent agent-1 is degraded (no heartbeat for 15s)
```

**Wait another 15 seconds (30 total)...**

**Master logs:**
```
❌ Agent agent-1 is offline (no heartbeat for 30s)
📊 Cluster: 2 agents (1 healthy), 0 storage nodes (0 running) - degraded
```

✅ **Health Monitoring Works!** Master detects agent failures.

---

## Summary

**✅ What we tested:**
1. Master starts and listens for agents
2. Agent connects, registers, and sends heartbeats
3. Agent auto-reconnects on Master restart
4. Multiple agents can register
5. Master detects agent failures (degraded at 15s, offline at 30s)

**🎉 Phase 1 Foundation Complete!**

**Next:** Week 3 - Storage node spawning

---

## Troubleshooting

### "Address already in use" (Master)
Another process is using port 7000. Kill it:
```bash
lsof -ti:7000 | xargs kill
```

### "Connection refused" (Agent)
Master is not running. Start Master first.

### Agent doesn't reconnect
Check `master_host` in `agent-config.toml` matches Master address.

---

## Architecture So Far

```
┌─────────────────────────┐
│  Master (port 7000)     │
│  - Agent registry       │
│  - Health monitor       │
└───────────┬─────────────┘
            │ gRPC
    ┌───────┴────────┬────────────┐
    │                │            │
    ▼                ▼            ▼
┌─────────┐    ┌─────────┐  ┌─────────┐
│ Agent 1 │    │ Agent 2 │  │ Agent N │
│ ❤️ 5s   │    │ ❤️ 5s   │  │ ❤️ 5s   │
└─────────┘    └─────────┘  └─────────┘
```

**Status:** Foundation solid ✅  
**Ready for:** Storage node spawning (Week 3)
