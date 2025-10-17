import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Chip,
  Box,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  CheckCircle as RunningIcon,
  Cancel as StoppedIcon,
  Warning as WarningIcon,
  HourglassEmpty as StartingIcon,
} from '@mui/icons-material';
import { SystemHealth } from '../../types';

interface SystemOverviewProps {
  health: SystemHealth;
}

export const SystemOverview: React.FC<SystemOverviewProps> = ({ health }) => {
  const getStatusIcon = (status: SystemHealth['status']) => {
    switch (status) {
      case 'healthy':
        return <RunningIcon color="success" fontSize="small" />;
      case 'degraded':
        return <WarningIcon color="warning" fontSize="small" />;
      case 'unavailable':
        return <StoppedIcon color="error" fontSize="small" />;
    }
  };

  const getStatusColor = (status: SystemHealth['status']) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unavailable':
        return 'error';
    }
  };

  return (
    <Card sx={{ height: 400 }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>
        
        <Stack spacing={2} mt={2}>
          <Box>
            <Stack spacing={1}>
              {/* System Status Header */}
              <Stack direction="row" justifyContent="space-between" alignItems="center">
                <Stack direction="row" alignItems="center" spacing={1}>
                  {getStatusIcon(health.status)}
                  <Typography variant="subtitle1" fontWeight={600}>
                    Sutra AI System
                  </Typography>
                </Stack>
                <Chip
                  label={health.status.toUpperCase()}
                  size="small"
                  color={getStatusColor(health.status) as any}
                  variant="filled"
                />
              </Stack>

              {/* System Metrics */}
              <Stack spacing={0.5}>
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption" color="text.secondary">
                    Uptime
                  </Typography>
                  <Typography variant="caption">
                    {health.uptime}
                  </Typography>
                </Stack>
                
                <Stack direction="row" justifyContent="space-between">
                  <Typography variant="caption" color="text.secondary">
                    Last Update
                  </Typography>
                  <Typography variant="caption">
                    {new Date(health.last_update).toLocaleTimeString()}
                  </Typography>
                </Stack>
              </Stack>

              {/* Status Bar */}
              <LinearProgress
                variant="determinate"
                value={health.status === 'healthy' ? 100 : health.status === 'degraded' ? 50 : 0}
                color={health.status === 'healthy' ? 'success' : health.status === 'degraded' ? 'warning' : 'error'}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  bgcolor: 'rgba(255,255,255,0.1)',
                }}
              />
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};