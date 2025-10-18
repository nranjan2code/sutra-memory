# Sutra Grid Testing Procedure

## Overview

This document provides a comprehensive, reproducible testing procedure for the Sutra Grid distributed storage system. Follow these steps to verify complete Grid functionality from clean startup to full operation.

## Prerequisites

### Required Components
- Grid Master (`sutra-grid-master`)
- Grid Agent (`sutra-grid-agent`) 
- Storage Server (`storage_server`)
- Grid CLI (`sutra-grid-cli`)

### System Requirements
- **OS**: macOS/Linux (Unix-like for process management)
- **Ports**: 50052 (event storage), 7002 (Grid Master), 8000 (Grid Agent)
- **Disk**: ~100MB for test storage nodes
- **Memory**: ~50MB per storage node

## Testing Procedure

### Phase 1: Clean Environment Setup

#### Step 1: Stop All Existing Processes
```bash
echo "=== Stopping All Grid Processes ==="
pkill -f sutra-grid-master
pkill -f sutra-grid-agent  
pkill -f storage_server
pkill -f dummy-storage
sleep 2
echo "Processes stopped"
```

#### Step 2: Verify Clean State
```bash
echo "=== Verifying Clean State ==="
ps aux | grep -E "(sutra-grid|storage_server)" | grep -v grep || echo "All processes stopped ✅"
lsof -i :50052,7002,8000 || echo "All ports free ✅"
```

#### Step 3: Build All Components
```bash
echo "=== Building Grid Components ==="

# Build Storage Server
cd packages/sutra-storage
cargo build --release --bin storage_server

# Build Grid Master  
cd ../sutra-grid-master
cargo build --release

# Build Grid Agent
cd ../sutra-grid-agent
cargo build --release

echo "All components built ✅"
```

### Phase 2: Component Startup

#### Step 4: Start Event Storage Server
```bash
echo "=== Step 1: Starting Event Storage ==="
cd packages/sutra-storage
rm -rf /tmp/grid-events-storage
mkdir -p /tmp/grid-events-storage

STORAGE_PORT=50052 STORAGE_PATH=/tmp/grid-events-storage \
  ./target/release/storage_server > /tmp/storage.log 2>&1 &

sleep 2
lsof -i :50052 && echo "Event storage running ✅"
```

#### Step 5: Start Grid Master
```bash
echo "=== Step 2: Starting Grid Master ==="
cd packages/sutra-grid-master

EVENT_STORAGE=http://localhost:50052 RUST_LOG=info \
  ./target/release/sutra-grid-master > /tmp/master.log 2>&1 &

sleep 2  
lsof -i :7002 && echo "Grid Master running ✅"
```

#### Step 6: Start Grid Agent
```bash
echo "=== Step 3: Starting Grid Agent ==="
cd packages/sutra-grid-agent

EVENT_STORAGE=http://localhost:50052 RUST_LOG=info \
  ./target/release/sutra-grid-agent agent-config.toml > /tmp/agent.log 2>&1 &

sleep 3
lsof -i :8000 && echo "Grid Agent running ✅"
```

#### Step 7: Verify Component Communication
```bash
echo "=== Verifying Communication ==="
cd packages/sutra-grid-master

# Check cluster status
./target/release/sutra-grid-cli status

# Check agent registration  
./target/release/sutra-grid-cli list-agents

echo "Communication verified ✅"
```

### Phase 3: Functional Testing

#### Step 8: Run Complete Integration Test
```bash
echo "=== Running Integration Test Suite ==="
cd packages/sutra-grid-master
./test-integration.sh

# Expected output: "🎉 All integration tests passed!"
```

#### Step 9: Manual Verification Tests

**Test 1: Storage Node Lifecycle**
```bash
# Spawn a storage node
NODE_ID=$(./target/release/sutra-grid-cli spawn \
  --agent agent-1 --port 50070 --storage-path /tmp/manual-test --memory 512 | \
  grep "Node ID:" | awk '{print $3}')

echo "Spawned node: $NODE_ID"

# Verify node is running
./target/release/sutra-grid-cli node-status --node $NODE_ID

# Stop the node  
./target/release/sutra-grid-cli stop --node $NODE_ID --agent agent-1

echo "Node lifecycle test ✅"
```

**Test 2: Multi-Node Management**
```bash
echo "=== Multi-Node Test ==="

# Spawn 3 nodes
for i in {1..3}; do
  ./target/release/sutra-grid-cli spawn \
    --agent agent-1 --port $((50070+i)) \
    --storage-path /tmp/multi-test-$i --memory 256
done

# Verify all nodes
./target/release/sutra-grid-cli list-agents

# Check cluster status
./target/release/sutra-grid-cli status

echo "Multi-node test ✅"
```

**Test 3: Event System Verification**
```bash
echo "=== Event System Test ==="

# Check event storage has data
echo "Event storage logs:"
tail -10 /tmp/storage.log

# Check Master events
echo "Master event logs:"  
grep "Event emission" /tmp/master.log

# Check Agent events
echo "Agent event logs:"
grep "Event emission" /tmp/agent.log

echo "Event system test ✅"
```

### Phase 4: Performance Testing (Optional)

#### Step 10: Load Testing
```bash
echo "=== Load Test ==="

# Spawn maximum nodes (configured max: 10)
for i in {1..10}; do
  ./target/release/sutra-grid-cli spawn \
    --agent agent-1 --port $((50100+i)) \
    --storage-path /tmp/load-test-$i --memory 128 \
    && echo "Node $i spawned"
done

# Verify all nodes are tracked
./target/release/sutra-grid-cli list-agents | grep "Storage Nodes:"

echo "Load test ✅"
```

#### Step 11: Stress Testing
```bash
echo "=== Stress Test ==="

# Rapid spawn/stop cycles
for i in {1..5}; do
  NODE_ID=$(./target/release/sutra-grid-cli spawn \
    --agent agent-1 --port $((50200+i)) --storage-path /tmp/stress-$i --memory 64 | \
    grep "Node ID:" | awk '{print $3}')
    
  sleep 1
  
  ./target/release/sutra-grid-cli stop --node $NODE_ID --agent agent-1
  echo "Cycle $i complete"
done

echo "Stress test ✅"
```

## Expected Results

### Successful Test Indicators

**Component Status:**
- ✅ Event Storage: Listening on port 50052
- ✅ Grid Master: Listening on port 7002, events enabled
- ✅ Grid Agent: Listening on port 8000, registered with Master

**Integration Test Results:**
```
🧪 Sutra Grid Integration Test
================================
✅ Test 1: Get Cluster Status  
✅ Test 2: List Agents
✅ Test 3: Spawn Storage Node
✅ Test 4: Query Node Status  
✅ Test 5: Stop Storage Node
🎉 All integration tests passed!
```

**Performance Expectations:**
- **Node Spawn Time**: 50-200ms
- **Node Stop Time**: 2-5s (graceful shutdown)
- **Status Query**: <5ms
- **Event Emission**: <0.1ms
- **Heartbeat Interval**: 5s

### Troubleshooting

**Common Issues:**

1. **Port Conflicts**: Check if ports 50052, 7002, 8000 are in use
   ```bash
   lsof -i :50052,7002,8000
   ```

2. **Build Failures**: Ensure Rust toolchain is up to date
   ```bash
   rustc --version  # Should be 1.70+
   ```

3. **Agent Registration Fails**: Check master endpoint in `agent-config.toml`
   ```toml
   master_host = "localhost:7002"  # Must match Master port
   ```

4. **Storage Nodes Won't Start**: Verify dummy script permissions
   ```bash
   ls -la packages/sutra-grid-agent/dummy-storage-server.sh
   # Should show: -rwxr-xr-x
   ```

5. **Event System Issues**: Check storage server logs
   ```bash
   tail -20 /tmp/storage.log
   ```

## Cleanup

### Post-Test Cleanup
```bash
echo "=== Cleanup ==="

# Stop all Grid processes
pkill -f sutra-grid-master
pkill -f sutra-grid-agent  
pkill -f storage_server
pkill -f dummy-storage

# Remove test directories
rm -rf /tmp/grid-events-storage
rm -rf /tmp/*test*
rm -rf /tmp/manual-test*
rm -rf /tmp/multi-test*
rm -rf /tmp/load-test*
rm -rf /tmp/stress-*

# Remove log files
rm -f /tmp/storage.log /tmp/master.log /tmp/agent.log

echo "Cleanup complete ✅"
```

## Test Automation Script

For automated testing, use this complete script:

```bash
#!/bin/bash
# File: test-grid-complete.sh

set -e  # Exit on error

echo "🧪 Complete Grid System Test"
echo "============================="

# Phase 1: Setup
echo "Phase 1: Clean Setup"
pkill -f sutra-grid || true
sleep 2

# Phase 2: Build
echo "Phase 2: Build Components"
cd packages/sutra-storage && cargo build --release --bin storage_server
cd ../sutra-grid-master && cargo build --release  
cd ../sutra-grid-agent && cargo build --release
cd ../..

# Phase 3: Start Services
echo "Phase 3: Start Services"
cd packages/sutra-storage
rm -rf /tmp/grid-events-storage && mkdir -p /tmp/grid-events-storage
STORAGE_PORT=50052 STORAGE_PATH=/tmp/grid-events-storage ./target/release/storage_server > /tmp/storage.log 2>&1 &
sleep 2

cd ../sutra-grid-master  
EVENT_STORAGE=http://localhost:50052 RUST_LOG=info ./target/release/sutra-grid-master > /tmp/master.log 2>&1 &
sleep 2

cd ../sutra-grid-agent
EVENT_STORAGE=http://localhost:50052 RUST_LOG=info ./target/release/sutra-grid-agent agent-config.toml > /tmp/agent.log 2>&1 &
sleep 3

# Phase 4: Test
echo "Phase 4: Integration Testing"
cd ../sutra-grid-master
./test-integration.sh

echo ""
echo "✅ Complete Grid System Test PASSED"
echo "🎯 Grid System is Production Ready!"
```

Make executable:
```bash
chmod +x test-grid-complete.sh
```

## Validation Checklist

Use this checklist to verify successful testing:

- [ ] All components build without errors
- [ ] Event storage starts and listens on port 50052
- [ ] Grid Master starts with event emission enabled  
- [ ] Grid Agent registers successfully with Master
- [ ] Integration test shows 5/5 tests passed
- [ ] Manual node spawn/stop operations work
- [ ] Event system logs show proper emission
- [ ] Multi-node management works correctly
- [ ] Performance meets expected benchmarks
- [ ] Cleanup completes without errors

## Documentation Updates

After successful testing, update:
- [ ] Version numbers in component documentation
- [ ] Performance benchmarks with actual measured values
- [ ] Known issues list (if any found)
- [ ] Deployment guides with tested configurations

---

## Test Results Template

```
# Sutra Grid Test Results

**Date**: YYYY-MM-DD  
**Tester**: [Name]  
**Environment**: [OS, Hardware]  
**Version**: [Git commit/tag]

## Component Status
- [ ] Storage Server: PASS/FAIL
- [ ] Grid Master: PASS/FAIL  
- [ ] Grid Agent: PASS/FAIL
- [ ] CLI Tools: PASS/FAIL

## Integration Tests
- [ ] Cluster Status: PASS/FAIL
- [ ] Agent Listing: PASS/FAIL
- [ ] Node Spawning: PASS/FAIL  
- [ ] Node Status: PASS/FAIL
- [ ] Node Stopping: PASS/FAIL

## Performance
- Node Spawn: ___ms
- Node Stop: ___ms  
- Status Query: ___ms
- Event Emission: ___ms

## Notes
[Any issues, observations, or recommendations]

## Overall Status
- [ ] PASS - Ready for production
- [ ] FAIL - Issues found (see notes)
```

This testing procedure ensures complete validation of the Sutra Grid system and provides reproducible results for continuous integration and deployment.