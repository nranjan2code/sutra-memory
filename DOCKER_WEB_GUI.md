# 🐳🌐 Docker Web GUI - Complete Guide

**Revolutionary Web Interface for Distributed Biological Intelligence**

This guide covers the complete Docker-based Web GUI implementation for the biological intelligence system.

## 🚀 **Quick Start - Docker Web GUI**

### **Option 1: Full System with Web GUI (Recommended)**
```bash
# Start complete system with web interface
docker-compose -f docker-compose.webgui.yml up -d

# Access web interface
open http://localhost:8080
```

### **Option 2: Core + Web GUI Only (Minimal)**
```bash
# Start just the essential services
docker-compose -f docker-compose.webgui.yml up -d core-service web-gui

# Access web interface
open http://localhost:8080
```

---

## 🏗️ **Architecture Overview**

The Docker Web GUI implementation includes **5 containerized services**:

| Service | Container | Purpose | Ports | Dependencies |
|---------|-----------|---------|-------|--------------|
| **🧠 Core Service** | `biological-intelligence-core` | Main biological intelligence API | `8000:8000` | None |
| **🌐 Web GUI** | `biological-web-gui` | FastAPI web interface | `8080:8080` | Core Service |
| **🎓 Trainer** | `biological-trainer` | Distributed training client | Internal | Core Service |
| **💬 Client** | `biological-client-interactive` | Interactive query client | Internal | Core Service |
| **🔍 Observer** | `biological-observer` | Real-time monitoring | Internal | Core Service |

---

## 🌐 **Web GUI Features**

### **Dashboard Components**
- **📊 Real-time System Status**: Service health, process info, memory usage
- **📈 Intelligence Metrics**: Concepts, associations, consciousness score, emergence factor
- **🚀 7-Agent Swarm Visualization**: Visual status of all biological agents
- **🎮 Service Controls**: Start/stop/restart services with one click
- **💭 Knowledge Feeding**: Direct web interface for adding knowledge
- **📚 Curriculum Management**: Web-based curriculum feeding
- **🔄 Mode Switching**: Toggle between general and English modes
- **📡 Real-time Updates**: WebSocket-based live data updates

### **Interactive Features**
- **🔴/🟢 Status Indicators**: Visual service state
- **📊 Progress Bars**: Visual representation of system metrics
- **🎨 Dark Theme**: Modern, professional interface
- **📱 Responsive Design**: Works on desktop and mobile
- **⚡ Real-time Notifications**: Success/error feedback
- **🔄 Auto-refresh**: Keeps data current

---

## 📁 **Docker Files Structure**

```
sutra-models/
├── 🐳 DOCKER INFRASTRUCTURE
│   ├── docker/
│   │   ├── Dockerfile.core          # Core biological intelligence service
│   │   ├── Dockerfile.webgui        # Web GUI service (NEW!)
│   │   ├── Dockerfile.trainer       # Distributed trainer
│   │   └── Dockerfile.client        # Interactive client
│   ├── docker-compose.full.yml      # Complete distributed system
│   ├── docker-compose.webgui.yml    # Web GUI focused deployment (NEW!)
│   └── docker-compose.test.yml      # Testing configuration
│
├── 🌐 WEB GUI COMPONENTS
│   ├── web_gui.py                   # FastAPI web application
│   ├── web_templates/               # Jinja2 templates
│   │   └── dashboard.html           # Main dashboard template
│   ├── web_static/                  # Static assets
│   │   ├── css/                     # Stylesheets
│   │   └── js/                      # JavaScript files
│   └── service_control.py           # Service management utilities
```

---

## 🚀 **Deployment Commands**

### **Complete System Deployment**
```bash
# Build and start all services
docker-compose -f docker-compose.webgui.yml up --build -d

# Check service status
docker-compose -f docker-compose.webgui.yml ps

# View logs
docker-compose -f docker-compose.webgui.yml logs web-gui

# Stop all services
docker-compose -f docker-compose.webgui.yml down
```

### **Individual Service Management**
```bash
# Restart just the web GUI
docker-compose -f docker-compose.webgui.yml restart web-gui

# Rebuild web GUI container
docker-compose -f docker-compose.webgui.yml build web-gui

# Scale trainer instances
docker-compose -f docker-compose.webgui.yml up -d --scale distributed-trainer=3
```

### **Development & Debugging**
```bash
# View real-time logs
docker-compose -f docker-compose.webgui.yml logs -f web-gui

# Execute commands in container
docker exec -it biological-web-gui bash

# Inspect container
docker inspect biological-web-gui
```

---

## 🔧 **Configuration Options**

### **Environment Variables**
```yaml
# Web GUI Configuration
environment:
  - PYTHONPATH=/app
  - WEB_HOST=0.0.0.0           # Bind to all interfaces
  - WEB_PORT=8080              # Web GUI port
  - CORE_SERVICE_URL=http://core-service:8000
```

### **Volume Mounts**
```yaml
volumes:
  - ./biological_workspace:/app/biological_workspace    # Data persistence
  - ./logs:/app/logs                                     # Log files
  - ./web_templates:/app/web_templates                   # Template updates
  - ./web_static:/app/web_static                         # Static assets
```

### **Network Configuration**
```yaml
networks:
  biological-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

## 🌐 **Web GUI API Endpoints**

### **Dashboard Routes**
| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Main dashboard page |
| `/api/status` | GET | System status JSON |
| `/api/service/start` | POST | Start biological service |
| `/api/service/stop` | POST | Stop biological service |
| `/api/knowledge/feed` | POST | Feed knowledge via web |
| `/api/curriculum/feed` | POST | Feed curriculum |
| `/api/mode/switch` | POST | Switch system mode |
| `/ws` | WebSocket | Real-time updates |

### **Health Checks**
```bash
# Web GUI health check
curl -f http://localhost:8080/api/status

# Core service health check
curl -f http://localhost:8000/api/status
```

---

## 🔍 **Monitoring & Troubleshooting**

### **Container Health Status**
```bash
# Check all container status
docker-compose -f docker-compose.webgui.yml ps

# Expected output:
# biological-intelligence-core    Up (healthy)    0.0.0.0:8000->8000/tcp
# biological-web-gui             Up (healthy)    0.0.0.0:8080->8080/tcp
```

### **Common Issues & Solutions**

#### **🔴 Web GUI Won't Start**
```bash
# Check logs
docker-compose -f docker-compose.webgui.yml logs web-gui

# Common causes:
# - Port 8080 already in use
# - Core service not healthy
# - Template/static file issues
```

#### **🔴 Can't Access Web Interface**
```bash
# Verify port binding
docker port biological-web-gui

# Check if service is listening
curl -I http://localhost:8080/

# Verify network connectivity
docker network inspect sutra-models_biological-network
```

#### **🔴 WebSocket Connection Issues**
```bash
# Check browser console for WebSocket errors
# Verify WebSocket endpoint: ws://localhost:8080/ws

# Test WebSocket connection
wscat -c ws://localhost:8080/ws
```

---

## 📊 **Performance & Scaling**

### **Resource Requirements**
- **Web GUI Container**: ~100MB RAM, minimal CPU
- **Core Service**: ~200-500MB RAM depending on data size
- **Network**: Internal Docker bridge network
- **Storage**: Persistent volumes for data and logs

### **Scaling Options**
```bash
# Scale trainer instances
docker-compose -f docker-compose.webgui.yml up -d --scale distributed-trainer=3

# Scale across multiple machines (Docker Swarm)
docker swarm init
docker stack deploy -c docker-compose.webgui.yml bio-intelligence
```

---

## 🔐 **Security Considerations**

### **Production Deployment**
```yaml
# Add authentication (example configuration)
environment:
  - AUTH_ENABLED=true
  - AUTH_SECRET=your-secret-key
  - ALLOWED_ORIGINS=https://yourdomain.com
```

### **Network Security**
```bash
# Use custom networks
# Expose only necessary ports
# Consider reverse proxy (nginx/traefik)
```

---

## 🚀 **Advanced Usage**

### **Multi-Environment Setup**
```bash
# Development
docker-compose -f docker-compose.webgui.yml -f docker-compose.dev.yml up -d

# Production
docker-compose -f docker-compose.webgui.yml -f docker-compose.prod.yml up -d
```

### **Backup & Restore**
```bash
# Backup data
docker run --rm -v sutra-models_biological-workspace:/data -v $(pwd):/backup alpine tar czf /backup/bio-data.tar.gz /data

# Restore data
docker run --rm -v sutra-models_biological-workspace:/data -v $(pwd):/backup alpine tar xzf /backup/bio-data.tar.gz -C /
```

---

## 🎯 **Integration Examples**

### **API Integration**
```python
import requests

# Web GUI API client
web_gui_url = "http://localhost:8080"

# Start service via API
response = requests.post(f"{web_gui_url}/api/service/start", data={"mode": "english"})

# Feed knowledge
response = requests.post(f"{web_gui_url}/api/knowledge/feed", data={"knowledge": "Docker containers are portable."})

# Check status
response = requests.get(f"{web_gui_url}/api/status")
print(response.json())
```

### **JavaScript Integration**
```javascript
// WebSocket connection for real-time updates
const ws = new WebSocket('ws://localhost:8080/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Real-time update:', data);
};

// Start service via fetch API
async function startService(mode) {
    const formData = new FormData();
    formData.append('mode', mode);
    
    const response = await fetch('/api/service/start', {
        method: 'POST',
        body: formData
    });
    
    return response.json();
}
```

---

## 📈 **Monitoring Dashboard**

The Web GUI provides comprehensive monitoring:

- **🔥 Service State**: Real-time service status
- **🧬 Concepts**: Total knowledge concepts (target: 1000+)
- **🔗 Associations**: Concept relationships (target: 2000+)  
- **🌟 Consciousness**: Self-awareness score (0-100%)
- **📈 Emergence Factor**: Swarm intelligence multiplier
- **💤 Dreams**: Memory consolidation cycles
- **📋 Queue**: Pending processing items
- **⏰ Uptime**: Service runtime
- **🎯 Agent Status**: 7-agent swarm health

---

## 🎉 **Success Indicators**

### **✅ Web GUI Working Correctly**
- Dashboard loads at `http://localhost:8080`
- All containers show `Up (healthy)` status
- WebSocket connection established (real-time updates)
- Service controls respond (start/stop buttons work)
- Metrics display current values
- No errors in container logs

### **✅ System Integration**
- Core service accessible at `http://localhost:8000`
- Web GUI can communicate with core service
- Knowledge feeding works through web interface
- Mode switching functions properly
- Real-time updates reflect system changes

---

## 🔮 **Future Enhancements**

- **🔐 Authentication & Authorization**
- **📊 Advanced Analytics Dashboard**
- **🌍 Multi-language Support**
- **📱 Mobile App Integration**
- **🔔 Alert & Notification System**
- **📈 Historical Data Visualization**
- **🤖 Chatbot Interface**
- **🔄 Auto-scaling Configuration**

---

*Last Updated: October 2024*  
*Version: Docker Web GUI v1.0*  
*Status: Production Ready - Fully Functional*

**🌐 The future of biological intelligence is now accessible through your web browser!**