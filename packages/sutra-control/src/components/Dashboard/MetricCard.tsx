import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Stack,
  Chip,
  useTheme,
} from '@mui/material';
import { TrendingUp as TrendingUpIcon, TrendingDown as TrendingDownIcon } from '@mui/icons-material';
import { motion } from 'framer-motion';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  progress?: number;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  trend,
  icon,
  color,
  progress,
}) => {
  const theme = useTheme();

  const getTrendColor = () => {
    if (trend === 'up') {
      return color === 'error' || color === 'warning' ? 'error' : 'success';
    }
    return color === 'error' || color === 'warning' ? 'success' : 'error';
  };

  const TrendIcon = trend === 'up' ? TrendingUpIcon : TrendingDownIcon;

  return (
    <motion.div
      whileHover={{ y: -4 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
    >
      <Card
        sx={{
          height: '100%',
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: `linear-gradient(90deg, ${theme.palette[color].main}, ${theme.palette[color].light})`,
          },
        }}
      >
        <CardContent sx={{ pb: 2 }}>
          <Stack spacing={2}>
            {/* Header */}
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
              <Box>
                <Typography variant="h6" color="text.secondary" fontSize="0.875rem">
                  {title}
                </Typography>
                <Typography variant="h4" fontWeight={700} color="text.primary" mt={0.5}>
                  {value}
                </Typography>
              </Box>
              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 2,
                  bgcolor: `${color}.main`,
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {icon}
              </Box>
            </Stack>

            {/* Change Indicator */}
            <Stack direction="row" alignItems="center" justifyContent="space-between">
              <Chip
                icon={<TrendIcon fontSize="small" />}
                label={change}
                size="small"
                color={getTrendColor()}
                variant="filled"
                sx={{
                  height: 24,
                  fontSize: '0.75rem',
                  fontWeight: 600,
                }}
              />
              {progress !== undefined && (
                <Typography variant="caption" color="text.secondary">
                  {progress.toFixed(1)}%
                </Typography>
              )}
            </Stack>

            {/* Progress Bar */}
            {progress !== undefined && (
              <Box>
                <LinearProgress
                  variant="determinate"
                  value={Math.min(progress, 100)}
                  sx={{
                    height: 6,
                    borderRadius: 3,
                    bgcolor: `${color}.50`,
                    '& .MuiLinearProgress-bar': {
                      borderRadius: 3,
                      bgcolor: `${color}.main`,
                    },
                  }}
                />
              </Box>
            )}
          </Stack>
        </CardContent>
      </Card>
    </motion.div>
  );
};