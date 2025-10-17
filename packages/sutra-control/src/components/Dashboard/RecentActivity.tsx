import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Box,
  Chip,
  Avatar,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RestartIcon,
  Psychology as QueryIcon,
  Storage as DataIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const mockActivities = [
  {
    id: 1,
    type: 'component_start',
    title: 'API Server Started',
    description: 'Sutra API component successfully started on port 8000',
    time: '2 minutes ago',
    icon: <StartIcon />,
    color: 'success',
  },
  {
    id: 2,
    type: 'query',
    title: 'New Query Processed',
    description: 'Reasoning query about "machine learning concepts" completed',
    time: '5 minutes ago',
    icon: <QueryIcon />,
    color: 'primary',
  },
  {
    id: 3,
    type: 'data_update',
    title: 'Knowledge Base Updated',
    description: '15 new concepts and 8 associations added',
    time: '12 minutes ago',
    icon: <DataIcon />,
    color: 'info',
  },
  {
    id: 4,
    type: 'component_restart',
    title: 'Storage Engine Restarted',
    description: 'Automatic restart after configuration update',
    time: '1 hour ago',
    icon: <RestartIcon />,
    color: 'warning',
  },
];

export const RecentActivity: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>
        
        <Stack spacing={2} mt={2}>
          {mockActivities.map((activity, index) => (
            <motion.div
              key={activity.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  p: 2,
                  borderRadius: 2,
                  bgcolor: 'rgba(255,255,255,0.03)',
                  border: '1px solid rgba(255,255,255,0.08)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    bgcolor: 'rgba(255,255,255,0.06)',
                    transform: 'translateX(4px)',
                  },
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: `${activity.color}.main`,
                    width: 40,
                    height: 40,
                  }}
                >
                  {activity.icon}
                </Avatar>
                
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    {activity.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {activity.description}
                  </Typography>
                </Box>
                
                <Chip
                  label={activity.time}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem' }}
                />
              </Box>
            </motion.div>
          ))}
        </Stack>
        
        <Box sx={{ textAlign: 'center', mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Activity log is updated in real-time
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};