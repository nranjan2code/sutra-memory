import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Stack,
  Chip,
  useTheme,
} from '@mui/material';
import {
  Storage as StorageIcon,
  Memory as MemoryIcon,
  Speed as CpuIcon,
  Psychology as ConceptsIcon,
  AccountTree as AssociationsIcon,
  Timeline as TimelineIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

import { useAppStore } from '../../store';
import { MetricCard } from './MetricCard';
import { PerformanceChart } from './PerformanceChart';
import { SystemOverview } from './SystemOverview';
import { RecentActivity } from './RecentActivity';

export const Dashboard: React.FC = () => {
  const theme = useTheme();
  const { systemStatus, chartData } = useAppStore();

  if (!systemStatus) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100%"
        flexDirection="column"
        gap={2}
      >
        <motion.div
          animate={{ scale: [1, 1.1, 1] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <Box
            sx={{
              width: 60,
              height: 60,
              borderRadius: '16px',
              background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.8rem',
            }}
          >
            🧠
          </Box>
        </motion.div>
        <Typography variant="h6" color="text.secondary">
          Connecting to Sutra AI...
        </Typography>
        <LinearProgress sx={{ width: 200 }} />
      </Box>
    );
  }

  const metrics = [
    {
      title: 'Knowledge Items',
      value: `${systemStatus.metrics.knowledge_items}`,
      change: '+15',
      trend: 'up' as const,
      icon: <StorageIcon />,
      color: 'primary' as const,
      progress: Math.min((systemStatus.metrics.knowledge_items / 1000) * 100, 100),
    },
    {
      title: 'Connections',
      value: systemStatus.metrics.connections.toLocaleString(),
      change: '+8',
      trend: 'up' as const,
      icon: <ConceptsIcon />,
      color: 'success' as const,
      progress: Math.min((systemStatus.metrics.connections / 10000) * 100, 100),
    },
    {
      title: 'Activity Score',
      value: `${systemStatus.metrics.activity_score.toFixed(1)}%`,
      change: '+2.3%',
      trend: 'up' as const,
      icon: <AssociationsIcon />,
      color: 'info' as const,
      progress: systemStatus.metrics.activity_score,
    },
    {
      title: 'System Load',
      value: `${systemStatus.metrics.system_load.toFixed(1)}%`,
      change: systemStatus.metrics.system_load > 70 ? 'High' : 'Normal',
      trend: systemStatus.metrics.system_load > 70 ? 'up' as const : 'down' as const,
      icon: <CpuIcon />,
      color: systemStatus.metrics.system_load > 70 ? 'warning' as const : 'success' as const,
      progress: systemStatus.metrics.system_load,
    },
    {
      title: 'Memory Usage',
      value: `${systemStatus.metrics.memory_usage.toFixed(1)}%`,
      change: systemStatus.metrics.memory_usage > 80 ? 'High' : 'Normal',
      trend: systemStatus.metrics.memory_usage > 80 ? 'up' as const : 'down' as const,
      icon: <MemoryIcon />,
      color: systemStatus.metrics.memory_usage > 80 ? 'error' as const : 'success' as const,
      progress: systemStatus.metrics.memory_usage,
    },
    {
      title: 'Response Time',
      value: `${systemStatus.metrics.response_time_ms.toFixed(1)}ms`,
      change: systemStatus.metrics.response_time_ms < 100 ? 'Fast' : 'Slow',
      trend: systemStatus.metrics.response_time_ms < 100 ? 'down' as const : 'up' as const,
      icon: <TimelineIcon />,
      color: systemStatus.metrics.response_time_ms < 100 ? 'success' as const : 'warning' as const,
      progress: Math.min((systemStatus.metrics.response_time_ms / 1000) * 100, 100),
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      style={{ height: '100%' }}
    >
      <Box sx={{ height: '100%', overflow: 'auto' }}>
        {/* Header */}
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" fontWeight={700} gutterBottom>
              System Dashboard
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Real-time monitoring and insights for your Sutra AI system
            </Typography>
          </Box>
        </motion.div>

        {/* Metrics Grid */}
        <motion.div variants={itemVariants}>
          <Grid container spacing={3} sx={{ mb: 4 }}>
            {metrics.map((metric, index) => (
              <Grid item xs={12} sm={6} lg={4} key={metric.title}>
                <motion.div
                  variants={itemVariants}
                  transition={{ delay: index * 0.05 }}
                >
                  <MetricCard {...metric} />
                </motion.div>
              </Grid>
            ))}
          </Grid>
        </motion.div>

        {/* Charts and System Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} lg={8}>
            <motion.div variants={itemVariants}>
              <Card sx={{ height: 400 }}>
                <CardContent sx={{ height: '100%' }}>
                  <Typography variant="h6" gutterBottom>
                    Performance Metrics
                  </Typography>
                  <PerformanceChart data={chartData} />
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
          <Grid item xs={12} lg={4}>
            <motion.div variants={itemVariants}>
              <SystemOverview health={systemStatus.health} />
            </motion.div>
          </Grid>
        </Grid>

        {/* Recent Activity */}
        <motion.div variants={itemVariants}>
          <RecentActivity />
        </motion.div>
      </Box>
    </motion.div>
  );
};