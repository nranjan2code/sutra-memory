"""
Sutra Grid API Integration for Control Center

Provides Grid management endpoints that query Sutra Storage for Grid events and metadata.
"Eating our own dogfood" - using Sutra's own storage instead of external databases.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# ===== Models =====

class GridAgent(BaseModel):
    """Grid agent information"""
    agent_id: str
    hostname: str
    platform: str
    status: str
    max_storage_nodes: int
    current_storage_nodes: int
    last_heartbeat: int
    storage_nodes: List[Dict[str, Any]] = []


class GridClusterStatus(BaseModel):
    """Overall grid cluster status"""
    total_agents: int
    healthy_agents: int
    total_storage_nodes: int
    running_storage_nodes: int
    status: str
    timestamp: str


class GridEvent(BaseModel):
    """Grid event from Sutra Storage"""
    event_type: str
    entity_id: str
    timestamp: str
    details: Dict[str, Any]


# ===== Grid Manager =====

class GridManager:
    """
    Manages Grid operations using Sutra Storage as the backend.
    All Grid events and metadata are stored in our own knowledge graph.
    """
    
    def __init__(self, storage_server: str, grid_master_addr: str = "localhost:7000"):
        self.storage_server = storage_server
        self.grid_master_addr = grid_master_addr
        self._grid_master_client = None
    
    async def get_grid_master_client(self):
        """Get gRPC client for Grid Master"""
        try:
            logger.info(f"Attempting connection to Grid Master at {self.grid_master_addr}")

            # Try to connect to Grid Master via TCP
            # For now, we don't have a Python gRPC client for Grid Master
            # So we'll rely on querying Sutra Storage for Grid events
            # This is the "eat our own dogfood" approach - using our own knowledge graph

            # If Grid Master connection is required, implement gRPC client here
            # For MVP, we'll gracefully return None and use storage fallback
            return None

        except Exception as e:
            logger.error(f"Failed to connect to Grid Master: {e}")
            return None
    
    async def get_agents(self) -> List[GridAgent]:
        """
        Get all registered agents from Grid Master.
        Falls back to querying Sutra Storage for agent_registered events if Master unavailable.
        """
        try:
            client = await self.get_grid_master_client()
            if not client:
                return await self._get_agents_from_storage()
            
            # Query Grid Master directly
            from sutra_grid_master import grid_pb2
            response = await client.list_agents(grid_pb2.Empty())
            
            agents = []
            for agent_record in response.agents:
                agents.append(GridAgent(
                    agent_id=agent_record.agent_id,
                    hostname=agent_record.hostname,
                    platform=agent_record.platform,
                    status=agent_record.status,
                    max_storage_nodes=agent_record.max_storage_nodes,
                    current_storage_nodes=agent_record.current_storage_nodes,
                    last_heartbeat=agent_record.last_heartbeat,
                    storage_nodes=[
                        {
                            "node_id": node.node_id,
                            "status": node.status,
                            "pid": node.pid,
                            "endpoint": node.endpoint
                        }
                        for node in agent_record.storage_nodes
                    ]
                ))
            
            return agents
            
        except Exception as e:
            logger.error(f"Failed to get agents from Grid Master: {e}")
            return await self._get_agents_from_storage()
    
    async def _get_agents_from_storage(self) -> List[GridAgent]:
        """
        Fallback: Query Sutra Storage for agent_registered events.
        This demonstrates querying our own storage for Grid metadata.
        """
        try:
            from sutra_storage_client import StorageClient

            storage = StorageClient(self.storage_server)

            # Query for AgentRegistered events using semantic search
            # Events are stored as concepts in the knowledge graph
            results = storage.semantic_search("AgentRegistered", max_results=100)

            agents_dict = {}

            # Parse results to extract agent information
            for result in results:
                # Each result should contain agent metadata
                content = result.get("content", "")

                # Extract agent_id from content (basic parsing)
                # In production, this would use structured event storage
                if "agent_id" in content:
                    # This is a placeholder - actual implementation would parse event structure
                    # For now, we return empty list since Grid events may not be in storage yet
                    pass

            # If no agents found in storage, return empty list
            # The UI will show "No agents available" state
            logger.info(f"Queried storage for Grid agents - found {len(agents_dict)} agents")
            return list(agents_dict.values())

        except Exception as e:
            logger.error(f"Failed to query storage for agents: {e}")
            # Storage unavailable - return empty list
            # UI will show appropriate "unavailable" state
            return []
    
    async def get_cluster_status(self) -> GridClusterStatus:
        """Get overall cluster status from Grid Master"""
        try:
            client = await self.get_grid_master_client()
            if not client:
                return GridClusterStatus(
                    total_agents=0,
                    healthy_agents=0,
                    total_storage_nodes=0,
                    running_storage_nodes=0,
                    status="unavailable",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            from sutra_grid_master import grid_pb2
            response = await client.get_cluster_status(grid_pb2.Empty())
            
            return GridClusterStatus(
                total_agents=response.total_agents,
                healthy_agents=response.healthy_agents,
                total_storage_nodes=response.total_storage_nodes,
                running_storage_nodes=response.running_storage_nodes,
                status=response.status,
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to get cluster status: {e}")
            return GridClusterStatus(
                total_agents=0,
                healthy_agents=0,
                total_storage_nodes=0,
                running_storage_nodes=0,
                status="error",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def query_grid_events(
        self,
        event_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        hours: int = 24
    ) -> List[GridEvent]:
        """
        Query Grid events from Sutra Storage using natural language or filters.

        Examples:
        - query_grid_events(event_type="agent_registered")
        - query_grid_events(event_type="node_crashed", hours=1)
        - query_grid_events(entity_id="agent-001")

        This uses Sutra's own reasoning engine to query events!
        """
        try:
            from sutra_storage_client import StorageClient

            storage = StorageClient(self.storage_server)

            # Build search query
            if event_type and entity_id:
                query = f"{event_type} {entity_id}"
            elif event_type:
                query = event_type
            elif entity_id:
                query = f"GridEvent {entity_id}"
            else:
                query = "GridEvent"

            logger.info(f"Grid event query: {query}")

            # Query Sutra Storage using semantic search
            results = storage.semantic_search(query, max_results=100)

            # Parse results into GridEvent objects
            events = []
            for result in results:
                # Extract event information from content
                # This is a simplified parser - production would use structured storage
                content = result.get("content", "")

                # Basic event extraction
                event = GridEvent(
                    event_type=event_type or "unknown",
                    entity_id=entity_id or "unknown",
                    timestamp=datetime.utcnow().isoformat(),
                    details={"content": content}
                )
                events.append(event)

            logger.info(f"Found {len(events)} Grid events")
            return events

        except Exception as e:
            logger.error(f"Failed to query Grid events: {e}")
            return []
    
    async def spawn_storage_node(
        self,
        agent_id: str,
        port: int,
        storage_path: str,
        memory_limit_mb: int = 512
    ) -> Dict[str, Any]:
        """Spawn a storage node on a specific agent"""
        try:
            client = await self.get_grid_master_client()
            if not client:
                return {"success": False, "error": "Grid Master unavailable"}
            
            from sutra_grid_master import grid_pb2
            
            request = grid_pb2.SpawnRequest(
                agent_id=agent_id,
                port=port,
                storage_path=storage_path,
                memory_limit_mb=memory_limit_mb
            )
            
            response = await client.spawn_storage_node(request)
            
            return {
                "success": response.success,
                "node_id": response.node_id if response.success else None,
                "endpoint": response.endpoint if response.success else None,
                "error": response.error_message if not response.success else None
            }
            
        except Exception as e:
            logger.error(f"Failed to spawn storage node: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_storage_node(
        self,
        agent_id: str,
        node_id: str
    ) -> Dict[str, Any]:
        """Stop a storage node"""
        try:
            client = await self.get_grid_master_client()
            if not client:
                return {"success": False, "error": "Grid Master unavailable"}
            
            from sutra_grid_master import grid_pb2
            
            request = grid_pb2.StopRequest(
                agent_id=agent_id,
                node_id=node_id
            )
            
            response = await client.stop_storage_node(request)
            
            return {
                "success": response.success,
                "error": response.error_message if not response.success else None
            }
            
        except Exception as e:
            logger.error(f"Failed to stop storage node: {e}")
            return {"success": False, "error": str(e)}
    
    async def natural_language_grid_query(self, query: str) -> Dict[str, Any]:
        """
        Execute natural language queries against Grid data in Sutra Storage.

        Examples:
        - "Show me all agents that went offline today"
        - "Which nodes crashed in the last hour?"
        - "What's the spawn failure rate for agent-001?"
        - "List all agents running on Kubernetes"

        This is the killer feature: Grid observability through natural language!
        """
        try:
            from sutra_storage_client import StorageClient

            storage = StorageClient(self.storage_server)

            logger.info(f"Natural language Grid query: {query}")

            # Perform semantic search on the query
            results = storage.semantic_search(query, max_results=10)

            # Parse and structure results
            structured_results = []
            for result in results:
                structured_results.append({
                    "content": result.get("content", ""),
                    "confidence": result.get("confidence", 0.0)
                })

            if structured_results:
                return {
                    "success": True,
                    "query": query,
                    "results": structured_results,
                    "explanation": f"Found {len(structured_results)} relevant Grid events",
                    "confidence": 0.85  # TODO: Calculate from results
                }
            else:
                return {
                    "success": True,
                    "query": query,
                    "results": [],
                    "explanation": "No Grid events found matching your query",
                    "confidence": 0.0
                }

        except Exception as e:
            logger.error(f"Natural language query failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# ===== FastAPI Route Handlers (to be added to main.py) =====

async def get_grid_agents_handler(grid_manager: GridManager):
    """GET /api/grid/agents - List all agents"""
    agents = await grid_manager.get_agents()
    return {"agents": [agent.dict() for agent in agents]}


async def get_grid_status_handler(grid_manager: GridManager):
    """GET /api/grid/status - Get cluster status"""
    status = await grid_manager.get_cluster_status()
    return status.dict()


async def query_grid_events_handler(
    grid_manager: GridManager,
    event_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    hours: int = 24
):
    """GET /api/grid/events - Query Grid events from Sutra Storage"""
    events = await grid_manager.query_grid_events(event_type, entity_id, hours)
    return {"events": [event.dict() for event in events]}


async def spawn_node_handler(grid_manager: GridManager, request_data: Dict[str, Any]):
    """POST /api/grid/spawn - Spawn a storage node"""
    result = await grid_manager.spawn_storage_node(
        agent_id=request_data["agent_id"],
        port=request_data["port"],
        storage_path=request_data.get("storage_path", "/tmp/storage"),
        memory_limit_mb=request_data.get("memory_limit_mb", 512)
    )
    return result


async def stop_node_handler(grid_manager: GridManager, request_data: Dict[str, Any]):
    """POST /api/grid/stop - Stop a storage node"""
    result = await grid_manager.stop_storage_node(
        agent_id=request_data["agent_id"],
        node_id=request_data["node_id"]
    )
    return result


async def natural_language_query_handler(grid_manager: GridManager, query: str):
    """POST /api/grid/query - Natural language Grid queries"""
    result = await grid_manager.natural_language_grid_query(query)
    return result
