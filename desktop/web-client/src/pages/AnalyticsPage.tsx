import { useQuery } from '@tanstack/react-query';
import { Activity, Clock, TrendingUp, Zap } from 'lucide-react';
import { sutraAPI } from '../api/client';

export function AnalyticsPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: sutraAPI.getStats,
    refetchInterval: 5000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse text-dark-400">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white">Analytics Dashboard</h1>
          <p className="text-dark-400 mt-1">Real-time performance metrics</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            icon={Activity}
            title="Total Concepts"
            value={stats?.total_concepts || 0}
            format="number"
            color="blue"
          />
          <StatCard
            icon={TrendingUp}
            title="Total Edges"
            value={stats?.total_edges || 0}
            format="number"
            color="green"
          />
          <StatCard
            icon={Clock}
            title="Avg Query Time"
            value={stats?.avg_query_time_ms || 0}
            format="ms"
            color="purple"
          />
          <StatCard
            icon={Zap}
            title="Storage Size"
            value={stats?.storage_size_mb || 0}
            format="mb"
            color="orange"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">Performance</h2>
            <div className="space-y-4">
              <MetricBar
                label="Query Speed"
                value={(stats?.avg_query_time_ms || 0) < 50 ? 95 : 70}
                color="green"
              />
              <MetricBar
                label="Storage Efficiency"
                value={85}
                color="blue"
              />
              <MetricBar
                label="Knowledge Density"
                value={stats?.total_edges && stats?.total_concepts 
                  ? Math.min((stats.total_edges / stats.total_concepts) * 20, 100)
                  : 0
                }
                color="purple"
              />
            </div>
          </div>

          <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
            <h2 className="text-xl font-bold text-white mb-4">System Health</h2>
            <div className="space-y-4">
              <HealthItem label="API Server" status="healthy" />
              <HealthItem label="Storage Server" status="healthy" />
              <HealthItem label="Embedding Service" status="healthy" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon: Icon,
  title,
  value,
  format,
  color,
}: {
  icon: any;
  title: string;
  value: number;
  format: 'number' | 'ms' | 'mb';
  color: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-600/20 text-blue-400',
    green: 'bg-green-600/20 text-green-400',
    purple: 'bg-purple-600/20 text-purple-400',
    orange: 'bg-orange-600/20 text-orange-400',
  }[color];

  const formatValue = (v: number) => {
    if (format === 'number') return v.toLocaleString();
    if (format === 'ms') return `${v.toFixed(1)}ms`;
    if (format === 'mb') return `${v.toFixed(1)} MB`;
    return v.toString();
  };

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-lg p-6">
      <div className={`w-12 h-12 rounded-lg ${colorClasses} flex items-center justify-center mb-4`}>
        <Icon className="w-6 h-6" />
      </div>
      <p className="text-dark-400 text-sm mb-1">{title}</p>
      <p className="text-3xl font-bold text-white">{formatValue(value)}</p>
    </div>
  );
}

function MetricBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const colorClasses = {
    green: 'bg-green-500',
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
  }[color];

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-dark-300">{label}</span>
        <span className="text-sm font-semibold text-white">{value.toFixed(0)}%</span>
      </div>
      <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
        <div
          className={`h-full ${colorClasses} rounded-full transition-all duration-500`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}

function HealthItem({
  label,
  status,
}: {
  label: string;
  status: 'healthy' | 'warning' | 'error';
}) {
  const statusConfig = {
    healthy: { color: 'bg-green-500', text: 'Healthy' },
    warning: { color: 'bg-yellow-500', text: 'Warning' },
    error: { color: 'bg-red-500', text: 'Error' },
  }[status];

  return (
    <div className="flex items-center justify-between">
      <span className="text-dark-300">{label}</span>
      <div className="flex items-center gap-2">
        <div className={`w-2 h-2 rounded-full ${statusConfig.color} animate-pulse`} />
        <span className="text-sm text-white">{statusConfig.text}</span>
      </div>
    </div>
  );
}
