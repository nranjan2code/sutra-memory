/**
 * API client types and responses
 */

export interface APIError {
  message: string;
  code?: string;
  details?: unknown;
}

export interface ConceptResponse {
  id: string;
  content: string;
  confidence: number;
  strength: number;
  access_count: number;
  created_at: string;
  metadata?: Record<string, unknown>;
  neighbors: string[];
}

export interface EdgeResponse {
  source_id: string;
  target_id: string;
  confidence: number;
  edge_type: string;
}

export interface GraphResponse {
  nodes: ConceptResponse[];
  edges: EdgeResponse[];
  stats: {
    total_nodes: number;
    total_edges: number;
    average_confidence: number;
  };
}

export interface StatsResponse {
  total_concepts: number;
  total_edges: number;
  total_vectors: number;
  file_size: number;
  version: number;
}

export interface SearchRequest {
  query: string;
  limit?: number;
}

export interface PathRequest {
  start_id: string;
  end_id: string;
  max_depth?: number;
}

export interface NeighborhoodRequest {
  id: string;
  depth?: number;
}

export interface SimilarityRequest {
  id1: string;
  id2: string;
}
