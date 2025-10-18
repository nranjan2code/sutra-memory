# Week 3: Storage Node Spawning - Test Guide

Test the **storage node spawning and monitoring** features.

## What's New in Week 3

✅ **Agent spawns storage node processes**  
✅ **Tracks PIDs and monitors health**  
✅ **Auto-restarts crashed nodes (up to 3 times)**  
✅ **Reports node count in heartbeats**

---

## Test 1: Basic Spawning

### Terminal 1: Start Master

```bash
cd packages/sutra-grid-master
cargo run
```

### Terminal 2: Start Agent

```bash
cd packages/sutra-grid-agent
cargo run
```

**Expected Agent logs:**
```
🚀 Sutra Grid Agent v0.1.0 starting...
📄 Loading config from agent-config.toml
⚙️  Config: Agent ID: agent-1, Platform: desktop, Max Nodes: 10
🔌 Connecting to Master at localhost:7000
✅ Connected to Master
📝 Registering with Master...
✅ Registered with Master (Master v0.1.0, Agent: agent-1, Host: ...)
🧪 TEST: Spawning test storage node...
📦 Spawning storage node test-node-1 on port 50051
✅ Storage node test-node-1 spawned (PID: XXXXX, Port: 50051)
✅ TEST: Storage node spawned on port 50051 (PID: XXXXX)
🔍 Starting storage node monitor
💓 Starting heartbeat loop (interval: 5s)
```

**Expected Master logs:**
```
📝 Agent registration request: agent-1 (desktop)
✅ Agent registered: agent-1 (total agents: 1)
💓 Heartbeat from agent-1 (nodes: 1)  ← NOTE: 1 storage node!
📊 Cluster: 1 agents (1 healthy), 1 storage nodes (0 running) - healthy
```

✅ **Test passed!** Agent spawned a storage node and reported it to Master.

---

## Test 2: Verify Process is Running

**Terminal 3: Check process**

```bash
# Find the PID from Agent logs (e.g., 12345)
ps aux | grep dummy-storage-server
```

**Expected:**
```
user  12345  ... ./dummy-storage-server.sh --port 50051 --storage-path ./data/test-node-1 --node-id test-node-1
```

✅ **Storage node process is running!**

---

## Test 3: Kill Process and Watch Auto-Restart

### Kill the Storage Node

```bash
# Use PID from Agent logs
kill 12345
```

**Agent logs (within 10 seconds):**
```
⚠️  Storage node test-node-1 exited: ExitStatus(...)
🔄 Storage node test-node-1 crashed, restarting...
📦 Spawning storage node test-node-1 on port 50052
✅ Storage node test-node-1 spawned (PID: XXXXX, Port: 50052)
```

✅ **Auto-restart works!** Agent detected crash and restarted the node.

**Note:** Port increments because we assign sequential ports.

---

## Test 4: Multiple Restarts

### Kill it again

```bash
kill <NEW_PID>
```

**Agent logs:**
```
⚠️  Storage node test-node-1 exited: ExitStatus(...)
🔄 Storage node test-node-1 crashed, restarting...
📦 Spawning storage node test-node-1 on port 50053
✅ Storage node test-node-1 spawned (PID: XXXXX, Port: 50053)
```

✅ **Second restart works!**

### Kill a third time

Agent will restart again (port 50054).

### Kill a fourth time

**Agent logs:**
```
⚠️  Storage node test-node-1 exited: ExitStatus(...)
```

**No restart!** Max restarts (3) reached.

✅ **Restart limit works!**

---

## Test 5: Heartbeat Reports Node Count

**Master logs:**
```
💓 Heartbeat from agent-1 (nodes: 1)  ← When node is running
💓 Heartbeat from agent-1 (nodes: 0)  ← After node crashes (before restart)
💓 Heartbeat from agent-1 (nodes: 1)  ← After restart
```

✅ **Heartbeats correctly report storage node count!**

---

## Test 6: Spawn Multiple Nodes (Manual)

Edit `src/main.rs` to spawn 3 nodes:

```rust
// TEST: Spawn multiple storage nodes
for i in 1..=3 {
    let node_id = format!("test-node-{}", i);
    match agent.spawn_storage_node(node_id.clone()).await {
        Ok((port, pid)) => {
            log::info!("✅ TEST: Node {} spawned on port {} (PID: {})", node_id, port, pid);
        }
        Err(e) => {
            log::error!("❌ TEST: Failed to spawn {}: {}", node_id, e);
        }
    }
}
```

**Rebuild and run:**
```bash
cargo build && cargo run
```

**Expected:**
```
✅ TEST: Node test-node-1 spawned on port 50051 (PID: ...)
✅ TEST: Node test-node-2 spawned on port 50052 (PID: ...)
✅ TEST: Node test-node-3 spawned on port 50053 (PID: ...)
💓 Heartbeat from agent-1 (nodes: 3)
```

**Master shows:**
```
📊 Cluster: 1 agents (1 healthy), 3 storage nodes (0 running) - healthy
```

✅ **Multi-node spawning works!**

---

## Test 7: Verify Storage Paths Created

```bash
ls -la packages/sutra-grid-agent/data/
```

**Expected:**
```
drwxr-xr-x  test-node-1/
drwxr-xr-x  test-node-2/
drwxr-xr-x  test-node-3/
```

✅ **Storage directories created per node!**

---

## Architecture So Far

```
Master (7000)
   ↓ gRPC
Agent (agent-1)
   ├── Heartbeat every 5s (reports node count)
   ├── Process Monitor (checks every 10s)
   └── Storage Nodes:
       ├── test-node-1 (PID: 12345, Port: 50051)
       ├── test-node-2 (PID: 12346, Port: 50052)
       └── test-node-3 (PID: 12347, Port: 50053)
```

**What's Working:**
- ✅ Spawn storage nodes
- ✅ Track PIDs
- ✅ Monitor health (every 10s)
- ✅ Auto-restart on crash (max 3 times)
- ✅ Report node count in heartbeats
- ✅ Sequential port assignment
- ✅ Per-node storage directories

---

## Cleanup

**Stop Agent (Terminal 2):** Ctrl+C

**Check if processes are killed:**
```bash
ps aux | grep dummy-storage-server
```

**Expected:** No processes (Agent kills children on exit... actually, it doesn't automatically! That's a TODO)

**Manual cleanup:**
```bash
pkill -f dummy-storage-server
```

**Remove test data:**
```bash
rm -rf packages/sutra-grid-agent/data/
```

---

## Summary

**✅ Week 3 Complete!**

1. Agent spawns storage node processes ✅
2. Monitors PIDs and detects crashes ✅
3. Auto-restarts failed nodes (max 3x) ✅
4. Reports node count to Master ✅
5. Creates per-node storage directories ✅

**🎉 Foundation is SOLID!**

**Next (Week 4):**
- Master → Agent spawn requests
- Proper process cleanup on Agent shutdown
- Integration with real storage-server binary
- End-to-end test with Master + 3 Agents + 9 Storage nodes

---

## Troubleshooting

### "Permission denied: dummy-storage-server.sh"
```bash
chmod +x packages/sutra-grid-agent/dummy-storage-server.sh
```

### "No such file or directory: dummy-storage-server.sh"
Make sure you're running from `packages/sutra-grid-agent/` directory.

### Process not restarting
Check `restart_failed_nodes = true` in `agent-config.toml`.

### Too many restarts
Default max is 3. Process will not restart after 3rd crash.
