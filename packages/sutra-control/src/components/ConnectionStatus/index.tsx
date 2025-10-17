import React from 'react';
import { Box, Chip, CircularProgress, Tooltip } from '@mui/material';
import { Wifi as ConnectedIcon, WifiOff as DisconnectedIcon } from '@mui/icons-material';
import { useAppStore } from '../../store';

export const ConnectionStatus: React.FC = () => {
  const { connection } = useAppStore();

  const getStatusConfig = () => {
    if (connection.connecting) {
      return {
        label: 'Connecting',
        color: 'warning' as const,
        icon: <CircularProgress size={16} />,
        tooltip: 'Establishing WebSocket connection...',
      };
    }
    
    if (connection.connected) {
      return {
        label: 'Connected',
        color: 'success' as const,
        icon: <ConnectedIcon fontSize="small" />,
        tooltip: 'WebSocket connection active',
      };
    }
    
    return {
      label: 'Disconnected',
      color: 'error' as const,
      icon: <DisconnectedIcon fontSize="small" />,
      tooltip: connection.error || 'WebSocket connection lost',
    };
  };

  const statusConfig = getStatusConfig();

  return (
    <Tooltip title={statusConfig.tooltip} placement="bottom">
      <Chip
        icon={statusConfig.icon}
        label={statusConfig.label}
        color={statusConfig.color}
        size="small"
        variant="filled"
        sx={{
          height: 28,
          fontSize: '0.75rem',
          fontWeight: 500,
        }}
      />
    </Tooltip>
  );
};