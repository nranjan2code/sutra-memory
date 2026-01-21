import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export interface LearnRequest {
  content: string;
}

export interface LearnResponse {
  concept_id: string;
  message: string;
  confidence?: number;
}

export interface QueryRequest {
  query: string;
  max_results?: number;
}

export interface QueryResponse {
  answer: string;
  concepts: Concept[];
  reasoning_paths?: ReasoningPath[];
  took_ms: number;
}

export interface Concept {
  concept_id: string;
  content: string;
  confidence?: number;
  created_at?: string;
  semantic_type?: string;
}

export interface ReasoningPath {
  path: string[];
  confidence: number;
  explanation?: string;
}

export interface Stats {
  total_concepts: number;
  total_edges: number;
  avg_query_time_ms: number;
  storage_size_mb?: number;
}

// API functions
export const sutraAPI = {
  // Health check
  health: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Learn a new concept
  learn: async (content: string): Promise<LearnResponse> => {
    const response = await api.post<LearnResponse>('/v1/learn', { content });
    return response.data;
  },

  // Query for reasoning
  query: async (query: string, maxResults?: number): Promise<QueryResponse> => {
    const response = await api.post<QueryResponse>('/v1/reason', {
      query,
      max_results: maxResults,
    });
    return response.data;
  },

  // Get all concepts
  listConcepts: async (): Promise<Concept[]> => {
    const response = await api.get<{ concepts: Concept[] }>('/v1/concepts');
    return response.data.concepts || [];
  },

  // Get concept by ID
  getConcept: async (conceptId: string): Promise<Concept> => {
    const response = await api.get<Concept>(`/v1/concepts/${conceptId}`);
    return response.data;
  },

  // Delete concept
  deleteConcept: async (conceptId: string): Promise<void> => {
    await api.delete(`/v1/concepts/${conceptId}`);
  },

  // Get statistics
  getStats: async (): Promise<Stats> => {
    const response = await api.get<Stats>('/v1/stats');
    return response.data;
  },

  // Search concepts
  search: async (query: string): Promise<Concept[]> => {
    const response = await api.post<{ concepts: Concept[] }>('/v1/search', {
      query,
    });
    return response.data.concepts || [];
  },
};

export default api;
