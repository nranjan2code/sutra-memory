import React, { useEffect, useState } from 'react';
import {
  Chip,
  Tooltip,
  Box,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Category as SimpleIcon,
  Star as CommunityIcon,
  Diamond as EnterpriseIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { EditionInfo } from '../../types';

const API_BASE_URL = '/api';  // Use gateway proxy

export const EditionBadge: React.FC = () => {
  const [editionInfo, setEditionInfo] = useState<EditionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEditionInfo = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/edition`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setEditionInfo(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch edition');
        console.error('Failed to fetch edition info:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchEditionInfo();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchEditionInfo, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Chip
        size="small"
        icon={<CircularProgress size={16} color="inherit" />}
        label="Loading..."
        sx={{ ml: 1 }}
      />
    );
  }

  if (error || !editionInfo) {
    return (
      <Tooltip title={error || 'Edition info unavailable'}>
        <Chip
          size="small"
          icon={<WarningIcon />}
          label="Unknown"
          color="warning"
          sx={{ ml: 1 }}
        />
      </Tooltip>
    );
  }

  const getEditionConfig = () => {
    switch (editionInfo.edition) {
      case 'simple':
        return {
          label: 'Simple',
          color: 'default' as const,
          icon: <SimpleIcon fontSize="small" />,
          bgGradient: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
        };
      case 'community':
        return {
          label: 'Community',
          color: 'primary' as const,
          icon: <CommunityIcon fontSize="small" />,
          bgGradient: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
        };
      case 'enterprise':
        return {
          label: 'Enterprise',
          color: 'warning' as const,
          icon: <EnterpriseIcon fontSize="small" />,
          bgGradient: 'linear-gradient(135deg, #f59e0b 0%, #eab308 100%)',
        };
      default:
        return {
          label: 'Unknown',
          color: 'default' as const,
          icon: <SimpleIcon fontSize="small" />,
          bgGradient: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
        };
    }
  };

  const config = getEditionConfig();

  const tooltipContent = (
    <Box sx={{ p: 1 }}>
      <Typography variant="subtitle2" gutterBottom fontWeight="bold">
        {config.label} Edition
      </Typography>
      
      {!editionInfo.license_valid && (
        <Alert severity="error" sx={{ mb: 1, py: 0 }}>
          License Invalid or Expired
        </Alert>
      )}
      
      <Typography variant="caption" display="block" sx={{ mt: 1, mb: 0.5 }}>
        <strong>Rate Limits:</strong>
      </Typography>
      <Typography variant="caption" display="block">
        • Learn: {editionInfo.limits.learn_per_min}/min
      </Typography>
      <Typography variant="caption" display="block">
        • Reason: {editionInfo.limits.reason_per_min}/min
      </Typography>
      
      <Typography variant="caption" display="block" sx={{ mt: 1, mb: 0.5 }}>
        <strong>Capacity:</strong>
      </Typography>
      <Typography variant="caption" display="block">
        • Max Concepts: {editionInfo.limits.max_concepts.toLocaleString()}
      </Typography>
      <Typography variant="caption" display="block">
        • Dataset Size: {editionInfo.limits.max_dataset_gb} GB
      </Typography>
      
      {editionInfo.edition === 'enterprise' && (
        <>
          <Typography variant="caption" display="block" sx={{ mt: 1, mb: 0.5 }}>
            <strong>Features:</strong>
          </Typography>
          {editionInfo.features.ha_enabled && (
            <Typography variant="caption" display="block">
              ✓ High Availability
            </Typography>
          )}
          {editionInfo.features.grid_enabled && (
            <Typography variant="caption" display="block">
              ✓ Grid Orchestration
            </Typography>
          )}
          {editionInfo.features.multi_node && (
            <Typography variant="caption" display="block">
              ✓ Multi-Node Support
            </Typography>
          )}
        </>
      )}
      
      {editionInfo.license_expires && (
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          Expires: {new Date(editionInfo.license_expires).toLocaleDateString()}
        </Typography>
      )}
      
      {editionInfo.edition !== 'enterprise' && (
        <Typography
          variant="caption"
          display="block"
          sx={{
            mt: 1,
            pt: 1,
            borderTop: '1px solid rgba(255,255,255,0.1)',
            color: 'primary.light',
          }}
        >
          <a
            href={editionInfo.upgrade_url}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'inherit', textDecoration: 'none' }}
          >
            → Upgrade to {editionInfo.edition === 'simple' ? 'Community' : 'Enterprise'}
          </a>
        </Typography>
      )}
    </Box>
  );

  return (
    <Tooltip title={tooltipContent} arrow>
      <Chip
        size="small"
        icon={config.icon}
        label={config.label}
        sx={{
          ml: 1,
          background: config.bgGradient,
          color: 'white',
          fontWeight: 600,
          '& .MuiChip-icon': {
            color: 'white',
          },
          cursor: 'pointer',
          transition: 'transform 0.2s',
          '&:hover': {
            transform: 'scale(1.05)',
          },
        }}
      />
    </Tooltip>
  );
};

export default EditionBadge;
