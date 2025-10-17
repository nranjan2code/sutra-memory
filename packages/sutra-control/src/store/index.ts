import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import {
  SystemStatus,
  ChartDataPoint,
  ConnectionState,
  UserPreferences,
  ReasoningPath,
  KnowledgeNode,
  KnowledgeEdge,
} from '../types';

interface AppState {
  // Connection state
  connection: ConnectionState;
  setConnection: (state: Partial<ConnectionState>) => void;

  // System data
  systemStatus: SystemStatus | null;
  chartData: ChartDataPoint[];
  setSystemStatus: (status: SystemStatus) => void;
  addChartDataPoint: (point: ChartDataPoint) => void;

  // AI-specific data
  reasoningPaths: ReasoningPath[];
  knowledgeGraph: {
    nodes: KnowledgeNode[];
    edges: KnowledgeEdge[];
  };
  setReasoningPaths: (paths: ReasoningPath[]) => void;
  addReasoningPath: (path: ReasoningPath) => void;
  setKnowledgeGraph: (nodes: KnowledgeNode[], edges: KnowledgeEdge[]) => void;

  // UI state
  sidebarOpen: boolean;
  currentView: string;
  preferences: UserPreferences;
  setSidebarOpen: (open: boolean) => void;
  setCurrentView: (view: string) => void;
  setPreferences: (preferences: Partial<UserPreferences>) => void;

  // WebSocket functions
  ws: WebSocket | null;
  connectWebSocket: () => void;
  disconnectWebSocket: () => void;

  // Component control
  controlComponent: (component: string, action: 'start' | 'stop' | 'restart') => Promise<boolean>;
}

const MAX_CHART_POINTS = 50;

export const useAppStore = create<AppState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial connection state
      connection: {
        connected: false,
        connecting: false,
      },
      setConnection: (state) =>
        set((prev) => ({
          connection: { ...prev.connection, ...state },
        })),

      // Initial system state
      systemStatus: null,
      chartData: [],
      setSystemStatus: (status) => {
        set({ systemStatus: status });
        
        // Also add to chart data
        const chartPoint: ChartDataPoint = {
          time: new Date(status.metrics.timestamp).toLocaleTimeString(),
          cpu: status.metrics.system_load,
          memory: status.metrics.memory_usage,
          storage: status.metrics.activity_score,
          concepts: status.metrics.knowledge_items,
          associations: status.metrics.connections,
        };
        
        get().addChartDataPoint(chartPoint);
      },
      addChartDataPoint: (point) =>
        set((state) => ({
          chartData: [
            ...state.chartData.slice(-(MAX_CHART_POINTS - 1)),
            point,
          ],
        })),

      // AI-specific state
      reasoningPaths: [],
      knowledgeGraph: {
        nodes: [],
        edges: [],
      },
      setReasoningPaths: (paths) => set({ reasoningPaths: paths }),
      addReasoningPath: (path) =>
        set((state) => ({
          reasoningPaths: [path, ...state.reasoningPaths.slice(0, 19)],
        })),
      setKnowledgeGraph: (nodes, edges) =>
        set({ knowledgeGraph: { nodes, edges } }),

      // UI state
      sidebarOpen: true,
      currentView: 'dashboard',
      preferences: {
        theme: 'dark',
        refreshInterval: 2000,
        compactMode: false,
        notifications: true,
      },
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setCurrentView: (view) => set({ currentView: view }),
      setPreferences: (prefs) =>
        set((state) => ({
          preferences: { ...state.preferences, ...prefs },
        })),

      // WebSocket state
      ws: null,

      // WebSocket connection management
      connectWebSocket: () => {
        const { ws } = get();
        if (ws?.readyState === WebSocket.OPEN) return;

        set((state) => ({
          connection: { ...state.connection, connecting: true },
        }));

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        const newWs = new WebSocket(wsUrl);

        newWs.onopen = () => {
          console.log('WebSocket connected');
          set({
            ws: newWs,
            connection: {
              connected: true,
              connecting: false,
              error: undefined,
            },
          });
        };

        newWs.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            // Backend sends { health, metrics, timestamp }
            // We need to extract just health and metrics for SystemStatus
            if (data.health && data.metrics) {
              const systemStatus: SystemStatus = {
                health: data.health,
                metrics: data.metrics,
              };
              get().setSystemStatus(systemStatus);
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        newWs.onerror = (error) => {
          console.error('WebSocket error:', error);
          set((state) => ({
            connection: {
              ...state.connection,
              connected: false,
              connecting: false,
              error: 'Connection error',
            },
          }));
        };

        newWs.onclose = () => {
          console.log('WebSocket disconnected');
          set((state) => ({
            ws: null,
            connection: {
              ...state.connection,
              connected: false,
              connecting: false,
            },
          }));
          
          // Auto-reconnect after 3 seconds
          setTimeout(() => {
            get().connectWebSocket();
          }, 3000);
        };
      },

      disconnectWebSocket: () => {
        const { ws } = get();
        if (ws) {
          ws.close();
          set({
            ws: null,
            connection: {
              connected: false,
              connecting: false,
            },
          });
        }
      },

      // Component control
      controlComponent: async (component, action) => {
        try {
          const response = await fetch(`/api/components/${component}/${action}`, {
            method: 'POST',
          });
          const result = await response.json();
          return result.success;
        } catch (error) {
          console.error(`Error ${action}ing ${component}:`, error);
          return false;
        }
      },
    })),
    {
      name: 'sutra-control-store',
    }
  )
);

// Auto-connect WebSocket when store is created
useAppStore.getState().connectWebSocket();