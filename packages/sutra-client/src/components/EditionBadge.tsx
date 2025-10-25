import { useState, useEffect } from 'react'
import { Chip, Tooltip, Box, Typography, CircularProgress, Alert } from '@mui/material'
import {
  Workspace as SimpleIcon,
  Star as CommunityIcon,
  Diamond as EnterpriseIcon,
  Warning as WarningIcon,
} from '@mui/icons-material'
import { sutraApi } from '../services/api'
import type { EditionResponse } from '../types/api'

export default function EditionBadge() {
  const [edition, setEdition] = useState<EditionResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchEdition = async () => {
      try {
        const data = await sutraApi.getEdition()
        setEdition(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch edition')
        console.error('Failed to fetch edition:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchEdition()
    // Refresh every 5 minutes
    const interval = setInterval(fetchEdition, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <Chip
        size="small"
        icon={<CircularProgress size={12} sx={{ color: 'inherit' }} />}
        label="Loading..."
        sx={{ fontSize: '0.75rem', height: 24 }}
      />
    )
  }

  if (error || !edition) {
    return (
      <Tooltip title={error || 'Edition info unavailable'}>
        <Chip
          size="small"
          icon={<WarningIcon sx={{ fontSize: 16 }} />}
          label="Unknown"
          color="warning"
          sx={{ fontSize: '0.75rem', height: 24 }}
        />
      </Tooltip>
    )
  }

  const getEditionConfig = () => {
    switch (edition.edition) {
      case 'simple':
        return {
          label: 'Simple',
          icon: <SimpleIcon sx={{ fontSize: 16 }} />,
          bgGradient: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
        }
      case 'community':
        return {
          label: 'Community',
          icon: <CommunityIcon sx={{ fontSize: 16 }} />,
          bgGradient: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
        }
      case 'enterprise':
        return {
          label: 'Enterprise',
          icon: <EnterpriseIcon sx={{ fontSize: 16 }} />,
          bgGradient: 'linear-gradient(135deg, #f59e0b 0%, #eab308 100%)',
        }
      default:
        return {
          label: 'Unknown',
          icon: <SimpleIcon sx={{ fontSize: 16 }} />,
          bgGradient: 'linear-gradient(135deg, #64748b 0%, #94a3b8 100%)',
        }
    }
  }

  const config = getEditionConfig()

  const tooltipContent = (
    <Box sx={{ p: 1.5, maxWidth: 280 }}>
      <Typography variant="subtitle2" gutterBottom fontWeight="bold">
        {config.label} Edition
      </Typography>

      {!edition.license_valid && (
        <Alert severity="error" sx={{ mb: 1.5, py: 0.5, fontSize: '0.75rem' }}>
          License Invalid
        </Alert>
      )}

      <Box sx={{ mt: 1.5 }}>
        <Typography variant="caption" display="block" fontWeight="bold" gutterBottom>
          Rate Limits:
        </Typography>
        <Typography variant="caption" display="block" sx={{ pl: 1 }}>
          • Learn: {edition.limits.learn_per_min}/min
        </Typography>
        <Typography variant="caption" display="block" sx={{ pl: 1 }}>
          • Reason: {edition.limits.reason_per_min}/min
        </Typography>
      </Box>

      <Box sx={{ mt: 1.5 }}>
        <Typography variant="caption" display="block" fontWeight="bold" gutterBottom>
          Capacity:
        </Typography>
        <Typography variant="caption" display="block" sx={{ pl: 1 }}>
          • Max Concepts: {edition.limits.max_concepts.toLocaleString()}
        </Typography>
        <Typography variant="caption" display="block" sx={{ pl: 1 }}>
          • Dataset Size: {edition.limits.max_dataset_gb} GB
        </Typography>
      </Box>

      {edition.edition === 'enterprise' && (
        <Box sx={{ mt: 1.5 }}>
          <Typography variant="caption" display="block" fontWeight="bold" gutterBottom>
            Features:
          </Typography>
          {edition.features.ha_enabled && (
            <Typography variant="caption" display="block" sx={{ pl: 1 }}>
              ✓ High Availability
            </Typography>
          )}
          {edition.features.grid_enabled && (
            <Typography variant="caption" display="block" sx={{ pl: 1 }}>
              ✓ Grid Orchestration
            </Typography>
          )}
          {edition.features.multi_node && (
            <Typography variant="caption" display="block" sx={{ pl: 1 }}>
              ✓ Multi-Node
            </Typography>
          )}
        </Box>
      )}

      {edition.license_expires && (
        <Typography variant="caption" display="block" sx={{ mt: 1.5, fontStyle: 'italic' }}>
          Expires: {new Date(edition.license_expires).toLocaleDateString()}
        </Typography>
      )}

      {edition.edition !== 'enterprise' && (
        <Box
          sx={{
            mt: 1.5,
            pt: 1.5,
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography
            variant="caption"
            component="a"
            href={edition.upgrade_url}
            target="_blank"
            rel="noopener noreferrer"
            sx={{
              color: 'primary.light',
              textDecoration: 'none',
              '&:hover': { textDecoration: 'underline' },
            }}
          >
            → Upgrade to {edition.edition === 'simple' ? 'Community' : 'Enterprise'}
          </Typography>
        </Box>
      )}
    </Box>
  )

  return (
    <Tooltip title={tooltipContent} arrow placement="bottom-start">
      <Chip
        size="small"
        icon={config.icon}
        label={config.label}
        sx={{
          fontSize: '0.75rem',
          height: 24,
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
  )
}
