import { Menu, X } from 'lucide-react';
import { useUIStore } from '../store';
import { useQuery } from '@tanstack/react-query';
import { sutraAPI } from '../api/client';

export function Header() {
  const { sidebarOpen, toggleSidebar } = useUIStore();

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: sutraAPI.getStats,
    refetchInterval: 10000,
  });

  return (
    <header className="h-16 bg-dark-900 border-b border-dark-700 flex items-center justify-between px-6">
      <button
        onClick={toggleSidebar}
        className="p-2 rounded-lg hover:bg-dark-800 transition-colors"
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? (
          <X className="w-5 h-5 text-dark-400" />
        ) : (
          <Menu className="w-5 h-5 text-dark-400" />
        )}
      </button>

      {stats && (
        <div className="flex items-center gap-6 text-sm text-dark-400">
          <div className="flex items-center gap-2">
            <span className="text-dark-500">Concepts:</span>
            <span className="font-semibold text-white">{stats.total_concepts.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-dark-500">Edges:</span>
            <span className="font-semibold text-white">{stats.total_edges.toLocaleString()}</span>
          </div>
          {stats.avg_query_time_ms && (
            <div className="flex items-center gap-2">
              <span className="text-dark-500">Avg Query:</span>
              <span className="font-semibold text-white">{stats.avg_query_time_ms.toFixed(1)}ms</span>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
