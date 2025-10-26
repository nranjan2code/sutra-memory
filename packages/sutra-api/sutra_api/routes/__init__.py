"""
Routes package for Sutra API.

Contains endpoint handlers organized by feature.
"""

from .auth import router as auth_router
from .conversations import router as conversations_router
from .spaces import router as spaces_router
from .search import router as search_router
from .graph import router as graph_router

__all__ = ["auth_router", "conversations_router", "spaces_router", "search_router", "graph_router"]
