#!/usr/bin/env python3
"""
🌐 BIOLOGICAL INTELLIGENCE WEB GUI
FastAPI-based web interface for remote control and monitoring.

Provides all functionality of the terminal GUI through a web browser:
- Service control (start/stop/restart)
- Real-time monitoring dashboard
- Knowledge feeding interface
- Curriculum management
- 7-agent swarm visualization
- Pi hardware monitoring
"""

import asyncio
import json
import time
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import logging

from fastapi import FastAPI, WebSocket, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Import our components
try:
    from pi_config import PiConfig
    PI_MODE = True
except:
    PI_MODE = False
    
from service_control import find_biological_processes, stop_service, start_service


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Biological Intelligence Control Center",
    description="Web-based interface for biological intelligence management",
    version="1.0.0"
)

# Setup static files and templates
app.mount("/static", StaticFiles(directory="web_static"), name="static")
templates = Jinja2Templates(directory="web_templates")

# Global state
current_mode = "general"
websocket_connections = []


class WebGUIManager:
    """Manager for web-based biological intelligence control."""
    
    def __init__(self):
        self.workspace = Path("./biological_workspace")
        self.english_workspace = Path("./english_biological_workspace")
        
        # Use Pi config if available
        if PI_MODE:
            self.workspace = Path(PiConfig.HDD_WORKSPACE) / "biological_workspace"
            self.english_workspace = Path(PiConfig.HDD_WORKSPACE) / "english_biological_workspace"
    
    def get_workspace(self) -> Path:
        """Get current workspace based on mode."""
        return self.english_workspace if current_mode == "english" else self.workspace
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        processes = find_biological_processes()
        service_running = len(processes) > 0
        
        # Read state files
        workspace = self.get_workspace()
        state_path = workspace / "service_state.json"
        metrics_path = workspace / "metrics.json"
        
        service_state = {}
        metrics = {}
        
        try:
            if state_path.exists():
                with open(state_path, 'r') as f:
                    service_state = json.load(f)
        except:
            pass
            
        try:
            if metrics_path.exists():
                with open(metrics_path, 'r') as f:
                    metrics = json.load(f)
        except:
            pass
        
        # Process info
        process_info = {}
        if processes:
            proc = processes[0]
            try:
                process_info = {
                    'pid': proc.pid,
                    'memory_mb': proc.memory_info().rss / 1024 / 1024,
                    'cpu_percent': proc.cpu_percent(),
                    'start_time': datetime.fromtimestamp(proc.create_time()).isoformat()
                }
            except:
                process_info = {'pid': proc.pid}
        
        # Pi-specific hardware info
        hardware_info = {}
        if PI_MODE:
            pi_status = PiConfig.get_system_status()
            hardware_info = {
                'cpu_temp': pi_status['hardware']['cpu_temp'],
                'memory_info': pi_status['memory'],
                'disk_info': pi_status['disk'],
                'thermal_status': pi_status['thermal'],
                'optimal_batch_size': pi_status['performance']['optimal_batch_size']
            }
        
        return {
            'service_running': service_running,
            'service_state': service_state,
            'metrics': metrics,
            'process_info': process_info,
            'hardware_info': hardware_info,
            'mode': current_mode,
            'workspace': str(self.get_workspace()),
            'pi_mode': PI_MODE,
            'timestamp': datetime.now().isoformat()
        }


# Global manager instance
web_manager = WebGUIManager()


# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass  # Connection might be closed

manager = ConnectionManager()


# Routes

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page."""
    status = web_manager.get_system_status()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "status": status,
        "pi_mode": PI_MODE
    })


@app.get("/api/status")
async def get_status():
    """Get current system status API."""
    return JSONResponse(web_manager.get_system_status())


@app.post("/api/service/start")
async def start_service_api(mode: str = Form(...)):
    """Start biological service API."""
    global current_mode
    current_mode = mode
    
    workspace = str(web_manager.get_workspace())
    english_mode = mode == "english"
    
    try:
        success = start_service(workspace, english_mode)
        await manager.broadcast({
            "type": "service_status",
            "message": f"Service {'started' if success else 'failed to start'} in {mode} mode",
            "success": success
        })
        return {"success": success, "mode": mode}
    except Exception as e:
        logger.error(f"Error starting service: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/service/stop")
async def stop_service_api():
    """Stop biological service API."""
    try:
        success = stop_service()
        await manager.broadcast({
            "type": "service_status", 
            "message": f"Service {'stopped' if success else 'failed to stop'}",
            "success": success
        })
        return {"success": success}
    except Exception as e:
        logger.error(f"Error stopping service: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/knowledge/feed")
async def feed_knowledge_api(knowledge: str = Form(...)):
    """Feed knowledge to the system API."""
    if not web_manager.get_system_status()['service_running']:
        return {"success": False, "error": "Service must be running"}
    
    workspace = str(web_manager.get_workspace())
    cmd = ["python", "biological_feeder.py", "text", knowledge, "--workspace", workspace]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())
        success = result.returncode == 0
        
        await manager.broadcast({
            "type": "knowledge_fed",
            "message": f"Knowledge {'fed successfully' if success else 'failed to feed'}",
            "knowledge": knowledge[:100] + "..." if len(knowledge) > 100 else knowledge,
            "success": success
        })
        
        return {
            "success": success,
            "message": result.stdout if success else result.stderr
        }
    except Exception as e:
        logger.error(f"Error feeding knowledge: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/curriculum/feed")
async def feed_curriculum_api():
    """Feed curriculum API."""
    if not web_manager.get_system_status()['service_running']:
        return {"success": False, "error": "Service must be running"}
    
    try:
        if current_mode == "english":
            # Start English curriculum feeder
            subprocess.Popen(["./english_feeder.sh"], cwd=Path.cwd())
            message = "English curriculum feeding started"
        else:
            message = "General curriculum feeding not implemented via web yet"
            
        await manager.broadcast({
            "type": "curriculum_feeding",
            "message": message,
            "mode": current_mode
        })
        
        return {"success": True, "message": message}
    except Exception as e:
        logger.error(f"Error feeding curriculum: {e}")
        return {"success": False, "error": str(e)}


@app.post("/api/mode/switch")
async def switch_mode_api(new_mode: str = Form(...)):
    """Switch between general and English modes."""
    global current_mode
    old_mode = current_mode
    current_mode = new_mode
    
    await manager.broadcast({
        "type": "mode_switch",
        "message": f"Switched from {old_mode} to {new_mode} mode",
        "old_mode": old_mode,
        "new_mode": new_mode
    })
    
    return {"success": True, "old_mode": old_mode, "new_mode": new_mode}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic status updates
            status = web_manager.get_system_status()
            await websocket.send_json({
                "type": "status_update",
                "data": status
            })
            await asyncio.sleep(5)  # Update every 5 seconds
    except:
        manager.disconnect(websocket)


# Background tasks for monitoring
async def system_monitor():
    """Background task for system monitoring."""
    while True:
        try:
            status = web_manager.get_system_status()
            
            # Check for thermal issues on Pi
            if PI_MODE and status.get('hardware_info', {}).get('thermal_status', {}).get('emergency_shutdown'):
                await manager.broadcast({
                    "type": "emergency",
                    "message": "EMERGENCY: CPU temperature critical! Shutting down service!",
                    "temp": status['hardware_info']['thermal_status'].get('cpu_temp', 0)
                })
                # Emergency stop
                stop_service()
            
            await asyncio.sleep(30)  # Check every 30 seconds
        except Exception as e:
            logger.error(f"System monitor error: {e}")
            await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup."""
    asyncio.create_task(system_monitor())
    if PI_MODE:
        PiConfig.setup_directories()


# Create necessary directories for templates and static files
def setup_web_directories():
    """Setup web template and static directories."""
    Path("web_templates").mkdir(exist_ok=True)
    Path("web_static").mkdir(exist_ok=True)
    Path("web_static/css").mkdir(exist_ok=True)
    Path("web_static/js").mkdir(exist_ok=True)


if __name__ == "__main__":
    setup_web_directories()
    
    # Determine host and port
    host = PiConfig.WEB_HOST if PI_MODE else "127.0.0.1"
    port = PiConfig.WEB_PORT if PI_MODE else 8080
    
    print(f"🌐 Starting Biological Intelligence Web GUI on {host}:{port}")
    print(f"🥧 Pi Mode: {'Enabled' if PI_MODE else 'Disabled'}")
    print(f"🔗 Access via: http://{host}:{port}")
    
    uvicorn.run(app, host=host, port=port, log_level="info")