import React from 'react';
import { Box, useTheme, Typography } from '@mui/material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  AreaChart,
} from 'recharts';
import { ChartDataPoint } from '../../types';

interface PerformanceChartProps {
  data: ChartDataPoint[];
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({ data }) => {
  const theme = useTheme();

  if (!data || data.length === 0) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100%"
        flexDirection="column"
      >
        <Typography variant="h6" color="text.secondary">
          No performance data available
        </Typography>
        <Typography variant="body2" color="text.secondary" mt={1}>
          Data will appear once the system starts collecting metrics
        </Typography>
      </Box>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            bgcolor: 'background.paper',
            p: 2,
            borderRadius: 2,
            border: `1px solid ${theme.palette.divider}`,
            boxShadow: theme.shadows[4],
          }}
        >
          <Typography variant="subtitle2" gutterBottom>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography
              key={index}
              variant="body2"
              sx={{ color: entry.color }}
            >
              {entry.name}: {entry.value}
              {entry.name.includes('CPU') || entry.name.includes('Memory') ? '%' : ''}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  const formatYAxisTick = (value: number, dataKey: string) => {
    if (dataKey === 'storage') {
      return `${value} MB`;
    }
    if (dataKey === 'cpu' || dataKey === 'memory') {
      return `${value}%`;
    }
    return value.toString();
  };

  return (
    <Box sx={{ width: '100%', height: '100%', pt: 2 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <defs>
            <linearGradient id="cpuGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3} />
              <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="memoryGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.3} />
              <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0.05} />
            </linearGradient>
            <linearGradient id="storageGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={theme.palette.warning.main} stopOpacity={0.3} />
              <stop offset="95%" stopColor={theme.palette.warning.main} stopOpacity={0.05} />
            </linearGradient>
          </defs>
          
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke={theme.palette.divider}
            opacity={0.3}
          />
          
          <XAxis
            dataKey="time"
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
          />
          
          <YAxis
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: theme.palette.text.secondary }}
            domain={[0, 100]}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Legend
            wrapperStyle={{
              fontSize: '14px',
              color: theme.palette.text.primary,
            }}
          />
          
          <Area
            type="monotone"
            dataKey="cpu"
            stroke={theme.palette.primary.main}
            strokeWidth={2}
            fill="url(#cpuGradient)"
            name="CPU %"
          />
          
          <Area
            type="monotone"
            dataKey="memory"
            stroke={theme.palette.success.main}
            strokeWidth={2}
            fill="url(#memoryGradient)"
            name="Memory %"
          />
        </AreaChart>
      </ResponsiveContainer>
    </Box>
  );
};