/**
 * Core graph data types
 */

export interface Node {
  id: string;
  content: string;
  confidence: number;
  strength: number;
  accessCount: number;
  createdAt: string;
  metadata?: Record<string, unknown>;
  edgeCount: number;
  x?: number;
  y?: number;
  z?: number;
}

export interface Edge {
  id: string;
  sourceId: string;
  targetId: string;
  confidence: number;
  edgeType: 'causal' | 'temporal' | 'similarity' | 'hierarchical';
}

export interface Graph {
  nodes: Node[];
  edges: Edge[];
  stats: {
    totalNodes: number;
    totalEdges: number;
    averageConfidence: number;
  };
}

export interface GraphStats {
  totalConcepts: number;
  totalEdges: number;
  totalVectors: number;
  fileSize: number;
  version: number;
}

export interface PathResult {
  path: string[];
  length: number;
  confidence: number;
  concepts: Node[];
}

export interface NeighborhoodResult {
  center: Node;
  neighbors: Node[];
  edges: Edge[];
  depth: number;
}
