/**
 * Sutra Explorer API Client
 * Production-grade REST client with storage client integration
 */

import type { Node, Edge } from '../types/graph';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8100';

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  storage_clients: string[];
  timestamp: string;
}

export interface GraphResponse {
  nodes: Node[];
  edges: Edge[];
  total_nodes: number;
  total_edges: number;
  storage_name: string;
}

export interface SearchResponse {
  query: string;
  results: Node[];
  total_results: number;
}

export interface NeighborhoodResponse {
  center_id: string;
  depth: number;
  graph: GraphResponse;
}

export interface StatsResponse {
  storage_name: string;
  total_concepts: number;
  total_associations: number;
  avg_confidence: number;
  timestamp: string;
}

export class ExplorerAPI {
  private baseUrl: string;
  private defaultStorage: string;

  constructor(baseUrl: string = API_BASE_URL, defaultStorage: string = 'domain') {
    this.baseUrl = baseUrl;
    this.defaultStorage = defaultStorage;
  }

  /**
   * Health check with storage client status
   */
  async health(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * List available storage clients
   */
  async listStorages(): Promise<{ storages: string[]; default: string }> {
    const response = await fetch(`${this.baseUrl}/storages`);
    if (!response.ok) {
      throw new Error(`Failed to list storages: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get concepts from storage (paginated)
   */
  async getConcepts(params?: {
    storage?: string;
    limit?: number;
    offset?: number;
    minConfidence?: number;
  }): Promise<GraphResponse> {
    const queryParams = new URLSearchParams();
    queryParams.set('storage', params?.storage || this.defaultStorage);
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.offset) queryParams.set('offset', params.offset.toString());
    if (params?.minConfidence !== undefined) {
      queryParams.set('min_confidence', params.minConfidence.toString());
    }

    const response = await fetch(
      `${this.baseUrl}/concepts?${queryParams.toString()}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get concepts: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get concept by ID
   */
  async getConcept(id: string, storage?: string): Promise<Node> {
    const queryParams = new URLSearchParams();
    queryParams.set('storage', storage || this.defaultStorage);

    const response = await fetch(
      `${this.baseUrl}/concepts/${id}?${queryParams.toString()}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get concept: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get associations (edges) for a concept
   */
  async getAssociations(id: string, storage?: string): Promise<Edge[]> {
    const queryParams = new URLSearchParams();
    queryParams.set('storage', storage || this.defaultStorage);

    const response = await fetch(
      `${this.baseUrl}/associations/${id}?${queryParams.toString()}`
    );

    if (!response.ok) {
      throw new Error(`Failed to get associations: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Full-text search concepts
   */
  async search(
    query: string,
    params?: {
      storage?: string;
      limit?: number;
    }
  ): Promise<SearchResponse> {
    const queryParams = new URLSearchParams();
    queryParams.set('query', query);
    queryParams.set('storage', params?.storage || this.defaultStorage);
    if (params?.limit) queryParams.set('limit', params.limit.toString());

    const response = await fetch(
      `${this.baseUrl}/search?${queryParams.toString()}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get N-hop neighborhood around a concept
   */
  async getNeighborhood(
    id: string,
    params?: {
      storage?: string;
      depth?: number;
      maxNodes?: number;
    }
  ): Promise<NeighborhoodResponse> {
    const queryParams = new URLSearchParams();
    queryParams.set('concept_id', id);
    queryParams.set('storage', params?.storage || this.defaultStorage);
    if (params?.depth) queryParams.set('depth', params.depth.toString());
    if (params?.maxNodes) queryParams.set('max_nodes', params.maxNodes.toString());

    const response = await fetch(
      `${this.baseUrl}/neighborhood?${queryParams.toString()}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      throw new Error(`Failed to get neighborhood: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get storage statistics
   */
  async getStatistics(storage?: string): Promise<StatsResponse> {
    const storageName = storage || this.defaultStorage;
    const response = await fetch(`${this.baseUrl}/statistics/${storageName}`);

    if (!response.ok) {
      throw new Error(`Failed to get statistics: ${response.statusText}`);
    }

    return response.json();
  }
}
