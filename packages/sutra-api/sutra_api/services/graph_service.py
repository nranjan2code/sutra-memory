"""
Graph Service

Provides graph data extraction and visualization support for the Sutra AI platform.
Fetches reasoning paths, concept nodes, and associations from domain storage.
"""

from typing import List, Dict, Optional, Any, Set, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GraphNode:
    """Represents a node in the knowledge graph."""
    
    def __init__(
        self,
        id: str,
        content: str,
        concept_type: str = "concept",
        metadata: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None
    ):
        self.id = id
        self.content = content
        self.concept_type = concept_type
        self.metadata = metadata or {}
        self.confidence = confidence
        self.created_at = self.metadata.get("created_at")
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.concept_type,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "created_at": self.created_at
        }


class GraphEdge:
    """Represents an edge (association) in the knowledge graph."""
    
    def __init__(
        self,
        source: str,
        target: str,
        association_type: str,
        strength: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.source = source
        self.target = target
        self.association_type = association_type
        self.strength = strength
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "source": self.source,
            "target": self.target,
            "type": self.association_type,
            "strength": self.strength,
            "metadata": self.metadata
        }


class ReasoningPath:
    """Represents a reasoning path through the knowledge graph."""
    
    def __init__(
        self,
        path_id: str,
        concepts: List[str],
        associations: List[Tuple[str, str, str]],  # (source, target, type)
        confidence: float,
        reasoning_steps: Optional[List[str]] = None
    ):
        self.path_id = path_id
        self.concepts = concepts
        self.associations = associations
        self.confidence = confidence
        self.reasoning_steps = reasoning_steps or []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "path_id": self.path_id,
            "concepts": self.concepts,
            "associations": [
                {"source": src, "target": tgt, "type": atype}
                for src, tgt, atype in self.associations
            ],
            "confidence": self.confidence,
            "reasoning_steps": self.reasoning_steps
        }


class GraphService:
    """
    Service for extracting and visualizing knowledge graph data.
    
    This service provides methods to:
    - Extract reasoning paths from message metadata
    - Fetch concept details and associations
    - Build subgraphs around specific concepts
    - Generate visualization-ready graph data
    """
    
    def __init__(self, domain_storage_clients: Dict[str, Any]):
        """
        Initialize graph service.
        
        Args:
            domain_storage_clients: Map of storage names to storage client instances
        """
        self.domain_storages = domain_storage_clients
        
    async def get_message_reasoning_graph(
        self,
        message_metadata: Dict[str, Any],
        domain_storage: str,
        max_depth: int = 2
    ) -> Dict[str, Any]:
        """
        Extract reasoning graph from message metadata.
        
        Args:
            message_metadata: Message metadata containing reasoning_paths and concepts_used
            domain_storage: Name of domain storage to query
            max_depth: Maximum depth for expanding concepts
            
        Returns:
            Graph data with nodes and edges
        """
        if domain_storage not in self.domain_storages:
            raise ValueError(f"Domain storage '{domain_storage}' not found")
            
        storage = self.domain_storages[domain_storage]
        
        # Extract reasoning paths from metadata
        reasoning_paths = message_metadata.get("reasoning_paths", [])
        concepts_used = message_metadata.get("concepts_used", [])
        confidence = message_metadata.get("confidence", 0.0)
        
        # Build graph from reasoning paths
        nodes_dict = {}
        edges_list = []
        
        # Add concepts used in reasoning
        for concept_id in concepts_used:
            try:
                concept = await storage.get_concept(concept_id)
                if concept:
                    nodes_dict[concept_id] = GraphNode(
                        id=concept_id,
                        content=concept.content,
                        concept_type="domain_concept",
                        metadata=concept.metadata,
                        confidence=confidence
                    )
            except Exception as e:
                logger.warning(f"Failed to fetch concept {concept_id}: {e}")
                continue
        
        # Parse reasoning paths (if stored as structured data)
        for i, path_data in enumerate(reasoning_paths):
            if isinstance(path_data, dict):
                # Structured path data
                path_concepts = path_data.get("concepts", [])
                path_confidence = path_data.get("confidence", confidence)
                
                # Add concepts from path
                for concept_id in path_concepts:
                    if concept_id not in nodes_dict:
                        try:
                            concept = await storage.get_concept(concept_id)
                            if concept:
                                nodes_dict[concept_id] = GraphNode(
                                    id=concept_id,
                                    content=concept.content,
                                    concept_type="path_concept",
                                    metadata=concept.metadata,
                                    confidence=path_confidence
                                )
                        except Exception as e:
                            logger.warning(f"Failed to fetch path concept {concept_id}: {e}")
                            continue
                
                # Add edges between consecutive concepts in path
                for j in range(len(path_concepts) - 1):
                    edges_list.append(GraphEdge(
                        source=path_concepts[j],
                        target=path_concepts[j + 1],
                        association_type="reasoning_step",
                        strength=path_confidence,
                        metadata={"path_index": i, "step": j}
                    ))
        
        # If max_depth > 1, expand with associations
        if max_depth > 1:
            expanded_nodes, expanded_edges = await self._expand_concepts(
                storage,
                list(nodes_dict.keys()),
                depth=max_depth - 1
            )
            
            # Merge expanded data
            for node in expanded_nodes:
                if node.id not in nodes_dict:
                    nodes_dict[node.id] = node
                    
            edges_list.extend(expanded_edges)
        
        return {
            "nodes": [node.to_dict() for node in nodes_dict.values()],
            "edges": [edge.to_dict() for edge in edges_list],
            "reasoning_paths": reasoning_paths,
            "confidence": confidence,
            "concept_count": len(nodes_dict),
            "edge_count": len(edges_list)
        }
    
    async def get_concept_subgraph(
        self,
        concept_id: str,
        domain_storage: str,
        depth: int = 2,
        max_nodes: int = 50
    ) -> Dict[str, Any]:
        """
        Get subgraph around a specific concept.
        
        Args:
            concept_id: ID of central concept
            domain_storage: Name of domain storage to query
            depth: How many hops to expand
            max_nodes: Maximum number of nodes to return
            
        Returns:
            Graph data with nodes and edges
        """
        if domain_storage not in self.domain_storages:
            raise ValueError(f"Domain storage '{domain_storage}' not found")
            
        storage = self.domain_storages[domain_storage]
        
        # Fetch central concept
        try:
            central_concept = await storage.get_concept(concept_id)
            if not central_concept:
                raise ValueError(f"Concept {concept_id} not found")
        except Exception as e:
            raise ValueError(f"Failed to fetch concept {concept_id}: {e}")
        
        nodes_dict = {
            concept_id: GraphNode(
                id=concept_id,
                content=central_concept.content,
                concept_type="central_concept",
                metadata=central_concept.metadata
            )
        }
        edges_list = []
        
        # Expand from central concept
        expanded_nodes, expanded_edges = await self._expand_concepts(
            storage,
            [concept_id],
            depth=depth,
            max_nodes=max_nodes - 1  # -1 for central node
        )
        
        # Merge expanded data
        for node in expanded_nodes:
            if node.id not in nodes_dict:
                nodes_dict[node.id] = node
                
        edges_list.extend(expanded_edges)
        
        return {
            "nodes": [node.to_dict() for node in nodes_dict.values()],
            "edges": [edge.to_dict() for edge in edges_list],
            "central_concept": concept_id,
            "depth": depth,
            "concept_count": len(nodes_dict),
            "edge_count": len(edges_list)
        }
    
    async def get_reasoning_paths_for_query(
        self,
        query: str,
        domain_storage: str,
        max_paths: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get reasoning paths for a query (without executing full reasoning).
        
        Args:
            query: Query string
            domain_storage: Name of domain storage to query
            max_paths: Maximum number of paths to return
            
        Returns:
            List of reasoning path data
        """
        if domain_storage not in self.domain_storages:
            raise ValueError(f"Domain storage '{domain_storage}' not found")
            
        storage = self.domain_storages[domain_storage]
        
        # Find relevant concepts
        try:
            search_results = await storage.semantic_search(
                query,
                top_k=max_paths * 3  # Get more to find diverse paths
            )
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []
        
        # Build paths from search results
        paths = []
        for i, result in enumerate(search_results[:max_paths]):
            # Get associations for this concept
            try:
                associations = await storage.get_associations(result.id)
                
                path = ReasoningPath(
                    path_id=f"path_{i}",
                    concepts=[result.id],
                    associations=[],
                    confidence=result.similarity if hasattr(result, 'similarity') else 0.9,
                    reasoning_steps=[f"Found concept: {result.content[:100]}"]
                )
                
                # Add first-level associations
                for assoc in associations[:3]:  # Limit associations per concept
                    path.concepts.append(assoc.target_id)
                    path.associations.append((result.id, assoc.target_id, assoc.association_type))
                
                paths.append(path.to_dict())
                
            except Exception as e:
                logger.warning(f"Failed to get associations for {result.id}: {e}")
                continue
        
        return paths
    
    async def _expand_concepts(
        self,
        storage: Any,
        concept_ids: List[str],
        depth: int,
        max_nodes: int = 50
    ) -> Tuple[List[GraphNode], List[GraphEdge]]:
        """
        Expand concepts by following associations.
        
        Args:
            storage: Storage client
            concept_ids: Starting concept IDs
            depth: How many hops to expand
            max_nodes: Maximum number of nodes to return
            
        Returns:
            Tuple of (nodes, edges)
        """
        nodes_dict = {}
        edges_list = []
        visited = set(concept_ids)
        current_level = concept_ids
        
        for level in range(depth):
            if len(nodes_dict) >= max_nodes:
                break
                
            next_level = []
            
            for concept_id in current_level:
                if len(nodes_dict) >= max_nodes:
                    break
                    
                try:
                    # Get associations
                    associations = await storage.get_associations(concept_id)
                    
                    for assoc in associations:
                        target_id = assoc.target_id
                        
                        if target_id in visited:
                            continue
                            
                        visited.add(target_id)
                        next_level.append(target_id)
                        
                        # Fetch target concept
                        try:
                            target_concept = await storage.get_concept(target_id)
                            if target_concept:
                                nodes_dict[target_id] = GraphNode(
                                    id=target_id,
                                    content=target_concept.content,
                                    concept_type="associated_concept",
                                    metadata=target_concept.metadata
                                )
                                
                                # Add edge
                                edges_list.append(GraphEdge(
                                    source=concept_id,
                                    target=target_id,
                                    association_type=assoc.association_type,
                                    strength=assoc.strength if hasattr(assoc, 'strength') else 1.0,
                                    metadata={"level": level}
                                ))
                                
                        except Exception as e:
                            logger.warning(f"Failed to fetch associated concept {target_id}: {e}")
                            continue
                            
                except Exception as e:
                    logger.warning(f"Failed to get associations for {concept_id}: {e}")
                    continue
            
            current_level = next_level
            
            if not current_level:
                break
        
        return list(nodes_dict.values()), edges_list
    
    async def get_graph_statistics(
        self,
        domain_storage: str
    ) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph.
        
        Args:
            domain_storage: Name of domain storage to query
            
        Returns:
            Statistics dictionary
        """
        if domain_storage not in self.domain_storages:
            raise ValueError(f"Domain storage '{domain_storage}' not found")
            
        storage = self.domain_storages[domain_storage]
        
        # These would need to be implemented in the storage client
        # For now, return placeholder data
        return {
            "total_concepts": 0,  # await storage.count_concepts()
            "total_associations": 0,  # await storage.count_associations()
            "storage_name": domain_storage,
            "timestamp": datetime.utcnow().isoformat()
        }
