import { useState, useEffect } from 'react';
import type { Node, Edge } from '@types/graph';
import { explorerAPI } from '@services/api';

interface GraphDataResult {
  nodes: Node[];
  edges: Edge[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useGraphData(): GraphDataResult {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch initial concepts (limit 1000 for now)
      const concepts = await explorerAPI.getConcepts({ limit: 1000, offset: 0 });
      
      // Transform API response to Node type
      const nodeData: Node[] = concepts.map((c) => ({
        id: c.id,
        content: c.content,
        confidence: c.confidence,
        strength: c.strength,
        accessCount: c.access_count,
        createdAt: c.created_at,
        metadata: c.metadata,
        edgeCount: c.neighbors.length,
      }));

      setNodes(nodeData);

      // Fetch edges for loaded nodes
      const edgePromises = nodeData.slice(0, 100).map((node) =>
        explorerAPI.getAssociations(node.id).catch(() => [])
      );

      const edgeResults = await Promise.all(edgePromises);
      const allEdges: Edge[] = [];

      edgeResults.forEach((associations) => {
        associations.forEach((edge) => {
          allEdges.push({
            id: `${edge.source_id}-${edge.target_id}`,
            sourceId: edge.source_id,
            targetId: edge.target_id,
            confidence: edge.confidence,
            edgeType: (edge.edge_type as Edge['edgeType']) || 'similarity',
          });
        });
      });

      setEdges(allEdges);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load graph data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return {
    nodes,
    edges,
    loading,
    error,
    refetch: fetchData,
  };
}
