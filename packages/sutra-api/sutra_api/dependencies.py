"""
Dependency injection for custom binary protocol storage client.

Replaced gRPC with custom binary protocol for better performance.
Storage remains a separate service (distributed architecture maintained).
"""

import logging
import os
import time

from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)

# Track service start time
_start_time: float = time.time()
_storage_client = None
_user_storage_client = None


def init_dependencies(app: FastAPI) -> None:
    """
    Initialize storage client using custom binary protocol.
    
    Args:
        app: FastAPI application instance
    """
    global _storage_client, _user_storage_client
    
    logger.info("Initializing storage clients (custom binary protocol)...")
    
    try:
        # Import TCP storage client
        from sutra_storage_client import StorageClient
        
        # Domain storage (existing)
        server_address = os.environ.get("SUTRA_STORAGE_SERVER", "storage-server:50051")
        logger.info(f"Connecting to domain storage server at {server_address}")
        
        _storage_client = StorageClient(server_address)
        logger.info("Successfully connected to domain storage server")
        app.state.storage_client = _storage_client
        
        # User storage (new)
        user_server_address = os.environ.get("SUTRA_USER_STORAGE_SERVER", "user-storage-server:50051")
        logger.info(f"Connecting to user storage server at {user_server_address}")
        
        _user_storage_client = StorageClient(user_server_address)
        logger.info("Successfully connected to user storage server")
        app.state.user_storage_client = _user_storage_client
        
    except Exception as e:
        logger.error(f"Failed to initialize storage clients: {e}")
        raise RuntimeError(f"Storage client initialization failed: {e}")


def shutdown_dependencies(app: FastAPI) -> None:
    """
    Clean up dependencies during shutdown.
    
    Args:
        app: FastAPI application instance
    """
    # Flush domain storage
    if hasattr(app.state, "storage_client"):
        try:
            app.state.storage_client.flush()
            logger.info("Flushed domain storage and closed connection")
        except Exception as e:
            logger.warning(f"Error flushing domain storage: {e}")
        delattr(app.state, "storage_client")
    
    # Flush user storage
    if hasattr(app.state, "user_storage_client"):
        try:
            app.state.user_storage_client.flush()
            logger.info("Flushed user storage and closed connection")
        except Exception as e:
            logger.warning(f"Error flushing user storage: {e}")
        delattr(app.state, "user_storage_client")


def get_storage_client(request: Request):
    """
    Dependency to get domain storage client from request state.
    
    Args:
        request: FastAPI request containing app.state
    
    Returns:
        StorageClient instance for domain storage
    """
    return request.app.state.storage_client


def get_user_storage_client(request: Request):
    """
    Dependency to get user storage client from request state.
    
    Args:
        request: FastAPI request containing app.state
    
    Returns:
        StorageClient instance for user storage
    """
    return request.app.state.user_storage_client


def get_uptime() -> float:
    """
    Get service uptime in seconds.
    
    Returns:
        Uptime in seconds
    """
    return time.time() - _start_time


def get_search_service(request: Request):
    """
    Dependency to get search service with user storage client.
    
    Args:
        request: FastAPI request containing app.state
    
    Returns:
        SearchService instance
    """
    from .services.search_service import SearchService
    return SearchService(user_storage_client=request.app.state.user_storage_client)


def get_graph_service(request: Request):
    """
    Dependency to get graph service with domain storage clients.
    
    Args:
        request: FastAPI request containing app.state
    
    Returns:
        GraphService instance
    """
    from .services.graph_service import GraphService
    
    # For now, we have a single domain storage client
    # In the future, this could support multiple domain storages
    domain_storages = {
        "default": request.app.state.storage_client
    }
    
    return GraphService(domain_storage_clients=domain_storages)
