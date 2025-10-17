"""
Sutra Control Center - Secure Gateway
Acts as the only interface between external clients and internal Sutra AI systems.
All internal communication via gRPC is abstracted from clients.
"""

import asyncio
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json

import grpc
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import gRPC client for internal communication
from sutra_storage_client.client import StorageClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status - no internal details exposed"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"


class SystemHealth(BaseModel):
    """System health response - abstracts internal details"""
    status: ServiceStatus
    uptime: str
    last_update: str


class SystemMetrics(BaseModel):
    """System metrics - no internal service names or details"""
    knowledge_items: int = 0
    connections: int = 0
    activity_score: float = 0.0
    response_time_ms: float = 0.0
    system_load: float = 0.0
    memory_usage: float = 0.0
    timestamp: str


class ControlGateway:
    """Gateway that manages all internal system communication via gRPC"""
    
    def __init__(self):
        self.storage_server = os.getenv("SUTRA_STORAGE_SERVER", "localhost:50051")
        self._storage_client = None
        self.start_time = datetime.utcnow()
        
    async def get_storage_client(self) -> Optional[StorageClient]:
        """Get storage client with connection handling"""
        try:
            if not self._storage_client:
                self._storage_client = StorageClient(self.storage_server)
            return self._storage_client
        except Exception as e:
            logger.error(f"Storage connection failed: {e}")
            return None
    
    async def get_system_health(self) -> SystemHealth:
        """Get overall system health - abstracts internal components"""
        try:
            client = await self.get_storage_client()
            if client:
                health = client.health_check()
                status = ServiceStatus.HEALTHY if health.get('status') == 'healthy' else ServiceStatus.DEGRADED
            else:
                status = ServiceStatus.UNAVAILABLE
                
            uptime = str(datetime.utcnow() - self.start_time).split('.')[0]
            
            return SystemHealth(
                status=status,
                uptime=uptime,
                last_update=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return SystemHealth(
                status=ServiceStatus.UNAVAILABLE,
                uptime="unknown",
                last_update=datetime.utcnow().isoformat()
            )
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get system metrics - no internal details exposed"""
        try:
            client = await self.get_storage_client()
            if not client:
                return SystemMetrics(timestamp=datetime.utcnow().isoformat())
            
            # Get storage stats via gRPC
            stats = client.stats()
            
            # Transform internal stats to abstract metrics
            return SystemMetrics(
                knowledge_items=stats.get('concepts', 0),
                connections=stats.get('edges', 0),
                activity_score=min(stats.get('written', 0) / 1000.0, 100.0),  # Normalize
                response_time_ms=1.0,  # Could measure actual response time
                system_load=min(stats.get('pending', 0) / 100.0, 100.0),  # Normalize
                memory_usage=50.0,  # Could get from system metrics
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return SystemMetrics(timestamp=datetime.utcnow().isoformat())
    
    async def execute_query(self, query_text: str) -> Dict[str, Any]:
        """Execute query against internal systems - abstract response"""
        try:
            client = await self.get_storage_client()
            if not client:
                return {"success": False, "error": "System unavailable"}
            
            # This would integrate with reasoning engine via gRPC
            # For now, return a placeholder that doesn't expose internals
            return {
                "success": True,
                "response": f"Query processed: {len(query_text)} characters",
                "processing_time_ms": 150,
                "confidence": 0.85
            }
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"success": False, "error": "Query processing failed"}


# Initialize FastAPI app
app = FastAPI(
    title="Sutra AI Control Center",
    description="Secure gateway to Sutra AI system",
    version="2.0.0",
    # Remove docs in production to prevent API discovery
    docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url=None if os.getenv("ENVIRONMENT") == "production" else "/redoc"
)

# Configure CORS - restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"] if os.getenv("ENVIRONMENT") != "production" else [],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Mount static files for React app if available
import os
from fastapi.responses import FileResponse

# Mount assets directory
if os.path.exists("/app/build/assets"):
    app.mount("/assets", StaticFiles(directory="/app/build/assets"), name="assets")

# Initialize gateway
gateway = ControlGateway()

# Active WebSocket connections
active_connections: List[WebSocket] = []


@app.get("/", response_class=HTMLResponse)
async def serve_app():
    """Serve React application"""
    try:
        with open("/app/build/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse("<h1>Sutra AI Control Center</h1><p>System initializing...</p>")


@app.get("/health")
async def health_check():
    """Public health endpoint - no internal details"""
    health = await gateway.get_system_health()
    return health


@app.get("/api/metrics")
async def get_metrics():
    """Get system metrics - abstracted from internal services"""
    metrics = await gateway.get_system_metrics()
    return metrics


@app.post("/api/query")
async def execute_query(request: dict):
    """Execute query - abstracts internal processing"""
    query_text = request.get("query", "").strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text required")
    
    if len(query_text) > 1000:  # Prevent abuse
        raise HTTPException(status_code=400, detail="Query too long")
    
    result = await gateway.execute_query(query_text)
    return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates - no internal details exposed"""
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"Client connected. Active connections: {len(active_connections)}")
    
    try:
        while True:
            # Send abstracted system status
            health = await gateway.get_system_health()
            metrics = await gateway.get_system_metrics()
            
            data = {
                "health": health.dict(),
                "metrics": metrics.dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_json(data)
            await asyncio.sleep(2)  # Update every 2 seconds
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"Client disconnected. Active connections: {len(active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_connections:
            active_connections.remove(websocket)


# Serve PWA files explicitly before catch-all route
@app.get("/manifest.webmanifest")
async def serve_manifest():
    """Serve PWA manifest"""
    return FileResponse("/app/build/manifest.webmanifest", media_type="application/manifest+json")


@app.get("/registerSW.js")
async def serve_register_sw():
    """Serve service worker registration"""
    return FileResponse("/app/build/registerSW.js", media_type="application/javascript")


@app.get("/sw.js")
async def serve_sw():
    """Serve service worker"""
    return FileResponse("/app/build/sw.js", media_type="application/javascript")


@app.get("/workbox-{filename}")
async def serve_workbox(filename: str):
    """Serve workbox files"""
    return FileResponse(f"/app/build/workbox-{filename}", media_type="application/javascript")


# Catch-all route for React Router
@app.get("/{path:path}")
async def serve_react_app(path: str):
    """Serve React app for any route - SPA support"""
    try:
        with open("/app/build/index.html", "r") as f:
            return HTMLResponse(f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Application not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 9000)),
        log_level="info"
    )