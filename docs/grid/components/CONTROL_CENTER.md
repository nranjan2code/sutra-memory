# Sutra Grid Control Center

The **Sutra Control Center** provides a modern, web-based interface for managing and monitoring the distributed Sutra Grid storage system. Built with React and integrated with FastAPI, it offers real-time Grid observability and management capabilities.

## Overview

The Control Center integrates Grid management into the existing Sutra AI Control interface, providing:

- **Real-time monitoring** of Grid agents and storage nodes
- **Interactive management** through point-and-click operations  
- **Web-based interface** accessible from any modern browser
- **REST API integration** with comprehensive Grid endpoints
- **Natural language queries** for Grid observability (planned)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (React App)                      │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐  │
│  │   Dashboard     │ │ Grid Management │ │   Settings    │  │
│  │                 │ │                 │ │               │  │
│  └─────────────────┘ └─────────────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │ HTTP/WebSocket
┌─────────────────────────────────────────────────────────────┐
│              Control Center Backend (FastAPI)               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌───────────────┐  │
│  │  Grid API       │ │  Health Check   │ │  WebSocket    │  │
│  │  (/api/grid/*)  │ │  (/health)      │ │  (/ws)        │  │
│  └─────────────────┘ └─────────────────┘ └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │ gRPC
┌─────────────────────────────────────────────────────────────┐
│                    Grid Master                              │
│              (localhost:7000)                               │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. **Grid Dashboard**
- **Cluster Overview**: Real-time metrics showing total and healthy agents
- **Storage Nodes**: Count of total and running storage nodes
- **System Health**: Overall Grid cluster status
- **Auto-refresh**: Updates every 10 seconds

### 2. **Agent Management**
- **Agent List**: Expandable view of all registered Grid agents
- **Agent Details**: Hostname, platform, status, and capacity information
- **Storage Node View**: Detailed information about nodes running on each agent
- **Status Indicators**: Color-coded status chips for quick health assessment

### 3. **Storage Node Operations**
- **Spawn Nodes**: Interactive dialog for creating new storage nodes
- **Stop Nodes**: One-click node termination
- **Configuration**: Customizable port, storage path, and memory limits
- **Real-time Updates**: Immediate UI refresh after operations

### 4. **Error Handling**
- **Graceful Degradation**: Continues working when Grid Master is unavailable
- **User Feedback**: Clear error messages and recovery suggestions
- **Fallback Data**: Mock data display for testing and development

## Access and Navigation

### Starting the Control Center

1. **Prerequisites**: Ensure Grid components are running
   ```bash
   # Start Grid Storage Server (for events)
   cd packages/sutra-storage && ./bootstrap-grid-events.sh
   
   # Start Grid Master
   cd packages/sutra-grid-master
   cargo run --release
   
   # Start Grid Agent
   cd packages/sutra-grid-agent  
   cargo run --release
   ```

2. **Start Control Center**:
   ```bash
   cd packages/sutra-control
   
   # Install dependencies (first time)
   npm install
   python3 -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn pydantic grpcio
   
   # Build frontend
   npm run build
   
   # Start backend
   SUTRA_GRID_MASTER=localhost:7000 python3 backend/main.py
   ```

3. **Access Interface**: Open http://localhost:9000 in your browser

### Navigation

- **Dashboard**: Main system overview
- **Grid Management**: Click "Grid Management" in the sidebar
- **Grid Icon**: Look for the grid/cluster icon in the navigation menu

## API Endpoints

The Control Center exposes comprehensive REST API endpoints for Grid management:

### **GET /api/grid/agents**
List all registered Grid agents.

**Response**:
```json
{
  "agents": [
    {
      "agent_id": "agent-001",
      "hostname": "localhost", 
      "platform": "macOS",
      "status": "healthy",
      "max_storage_nodes": 5,
      "current_storage_nodes": 2,
      "last_heartbeat": 1760755569,
      "storage_nodes": [
        {
          "node_id": "node-001",
          "status": "running",
          "pid": 12345,
          "endpoint": "localhost:50053"
        }
      ]
    }
  ]
}
```

### **GET /api/grid/status**
Get overall Grid cluster status.

**Response**:
```json
{
  "total_agents": 1,
  "healthy_agents": 1,
  "total_storage_nodes": 2,
  "running_storage_nodes": 2,
  "status": "healthy",
  "timestamp": "2025-10-18T08:16:20.573481"
}
```

### **GET /api/grid/events**
Query Grid events with optional filters.

**Parameters**:
- `event_type` (optional): Filter by event type
- `entity_id` (optional): Filter by entity ID  
- `hours` (optional): Time window in hours (default: 24)

### **POST /api/grid/spawn**
Spawn a new storage node on an agent.

**Request**:
```json
{
  "agent_id": "agent-001",
  "port": 50053,
  "storage_path": "/tmp/storage",
  "memory_limit_mb": 512
}
```

### **POST /api/grid/stop**
Stop a running storage node.

**Request**:
```json
{
  "agent_id": "agent-001", 
  "node_id": "node-001"
}
```

### **POST /api/grid/query**
Execute natural language queries against Grid data (future feature).

**Request**:
```json
{
  "query": "Show me all agents that went offline today"
}
```

## Configuration

### Environment Variables

```bash
# Grid Master address (default: localhost:7000)  
export SUTRA_GRID_MASTER="localhost:7000"

# Storage Server address (default: localhost:50051)
export SUTRA_STORAGE_SERVER="localhost:50051"

# Control Center port (default: 9000)
export PORT="9000"

# Environment mode
export ENVIRONMENT="development"  # or "production"
```

### Development vs Production

**Development Mode**:
- API documentation available at `/docs`
- CORS enabled for `localhost:3000`
- Mock data fallbacks for testing
- Detailed error messages

**Production Mode**:
- API documentation disabled
- Restricted CORS policy
- Enhanced security headers
- Minimal error exposure

## User Interface Guide

### Grid Management Dashboard

1. **Cluster Status Cards**:
   - **Total Agents**: Number of registered agents
   - **Healthy Agents**: Agents responding to heartbeats
   - **Storage Nodes**: Total nodes across all agents
   - **Running Nodes**: Currently active storage nodes

2. **Agent List**:
   - **Expandable Cards**: Click to view agent details
   - **Status Badges**: Color-coded health indicators
   - **Node Count**: Current/maximum storage nodes per agent
   - **Platform Info**: Operating system and hostname

3. **Storage Node Details**:
   - **Node ID**: Unique identifier for each storage node
   - **Status**: Current operational state
   - **PID**: Process ID for monitoring
   - **Endpoint**: Network address and port
   - **Stop Button**: One-click node termination

4. **Spawn Node Dialog**:
   - **Agent Selection**: Choose target agent from dropdown
   - **Port Configuration**: Specify network port for new node
   - **Storage Path**: Set data storage directory
   - **Memory Limit**: Configure memory allocation in MB

### Keyboard Shortcuts

- **Refresh**: Click the refresh icon or wait for auto-refresh
- **Quick Spawn**: Use the "Spawn Node" button in the header
- **Navigation**: Use sidebar menu for switching between views

## Integration with Existing Grid Components

### Grid Master Communication

The Control Center communicates with the Grid Master via gRPC:

1. **Direct Queries**: Real-time agent status and cluster information
2. **Operation Commands**: Node spawn/stop operations
3. **Fallback Mode**: When Grid Master is unavailable, uses Sutra Storage for historical data

### Event Integration

Integration with the Grid event system provides:

1. **Historical Queries**: Access to past Grid events via Sutra Storage
2. **Natural Language**: Query events using plain English (planned)
3. **Audit Trails**: Complete operational history and compliance

### Storage Integration  

Uses Sutra's own storage for Grid metadata ("eating our own dogfood"):

1. **Event Storage**: All Grid events stored in Sutra Storage  
2. **Query Engine**: Leverages Sutra's reasoning engine for Grid analytics
3. **Self-Hosting**: Grid observability through Sutra's own technology

## Troubleshooting

### Common Issues

**Grid Master Connection Failed**:
```
INFO:grid_api:Attempting connection to Grid Master at localhost:7000
```
- **Solution**: Ensure Grid Master is running on the specified port
- **Fallback**: Control Center will use mock data for testing

**Backend Import Errors**:
```
ModuleNotFoundError: No module named 'pydantic'
```
- **Solution**: Install Python dependencies in virtual environment
  ```bash
  pip install fastapi uvicorn pydantic grpcio
  ```

**Frontend Build Errors**:
```
error TS2440: Import declaration conflicts with local declaration
```
- **Solution**: Already fixed - Grid component uses `MuiGrid` alias

**API Endpoints Not Found**:
- **Check**: Backend is running on correct port (9000)
- **Verify**: PYTHONPATH includes the control package directory

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL="DEBUG"
python3 backend/main.py
```

View browser console for frontend debugging:
- **Chrome**: F12 → Console tab
- **Firefox**: F12 → Console tab  
- **Safari**: Develop → Show Web Inspector

## Security Considerations

### Production Deployment

1. **HTTPS Only**: Configure reverse proxy with SSL certificates
2. **Authentication**: Add user authentication and role-based access
3. **Network Security**: Restrict Grid Master access to control network
4. **Input Validation**: All API inputs are validated via Pydantic models

### Access Control

- **Internal Network**: Deploy Control Center on internal/management network
- **VPN Access**: Require VPN for external access
- **Audit Logging**: All operations logged for compliance

## Future Enhancements

### Phase 2 Features

1. **Natural Language Queries**: 
   - "Show me nodes that crashed today"  
   - "Which agents have high memory usage?"
   - "List all spawn failures in the last hour"

2. **Advanced Visualizations**:
   - Network topology diagrams
   - Real-time performance charts
   - Capacity planning dashboards  

3. **Automated Operations**:
   - Auto-scaling based on load
   - Automatic failover and recovery
   - Scheduled maintenance operations

4. **Integration Enhancements**:
   - Prometheus metrics export
   - Grafana dashboard templates
   - Kubernetes operator integration

## Related Documentation

- [Grid Architecture](../architecture/GRID_ARCHITECTURE.md) - Complete system architecture
- [Grid Testing](../operations/GRID_TESTING_PROCEDURE.md) - Comprehensive testing guide  
- [Event Integration](../events/EVENT_INTEGRATION.md) - Event-driven observability
- [Grid Master](MASTER.md) - Grid Master component details
- [Grid Agent](AGENT.md) - Grid Agent component details

---

*The Sutra Grid Control Center represents the culmination of Grid development - a production-ready, web-based interface that makes distributed storage management accessible and intuitive.*