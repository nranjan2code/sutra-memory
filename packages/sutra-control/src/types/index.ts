export interface SystemMetrics {
  timestamp: string;
  knowledge_items: number;
  connections: number;
  activity_score: number;
  response_time_ms: number;
  system_load: number;
  memory_usage: number;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unavailable';
  uptime: string;
  last_update: string;
}

export interface ComponentStatus {
  name: string;
  state: 'stopped' | 'starting' | 'running' | 'stopping' | 'error';
  pid?: number;
  uptime?: number;
  cpu_percent?: number;
  memory_mb?: number;
  error?: string;
  last_updated: string;
}

export interface SystemStatus {
  health: SystemHealth;
  metrics: SystemMetrics;
}

export interface MetricHistory {
  timestamp: string;
  value: number;
}

export interface ChartDataPoint {
  time: string;
  cpu: number;
  memory: number;
  storage: number;
  concepts: number;
  associations: number;
}

export interface KnowledgeNode {
  id: string;
  label: string;
  type: 'concept' | 'association';
  weight?: number;
  position?: { x: number; y: number };
}

export interface KnowledgeEdge {
  id: string;
  source: string;
  target: string;
  weight: number;
  type: string;
}

export interface ReasoningPath {
  id: string;
  query: string;
  steps: Array<{
    concept: string;
    confidence: number;
    reasoning: string;
  }>;
  finalAnswer: string;
  confidence: number;
  timestamp: string;
}

export interface ConnectionState {
  connected: boolean;
  connecting: boolean;
  error?: string;
}

export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
}

export type ThemeMode = 'light' | 'dark' | 'auto';

export interface UserPreferences {
  theme: ThemeMode;
  refreshInterval: number;
  compactMode: boolean;
  notifications: boolean;
}