import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Stack,
  Box,
  Chip,
  Avatar,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RestartIcon,
  Psychology as QueryIcon,
  Storage as DataIcon,
  ErrorOutline as ErrorIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface Activity {
  id: number;
  type: string;
  title: string;
  description: string;
  time: string;
  icon: React.ReactNode;
  color: 'success' | 'primary' | 'info' | 'warning' | 'error';
}

export const RecentActivity: React.FC = () => {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchActivities();

    // Poll for updates every 30 seconds
    const interval = setInterval(fetchActivities, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchActivities = async () => {
    try {
      // Query Grid events from backend
      const response = await fetch('/api/grid/events?hours=24');

      if (response.ok) {
        const data = await response.json();
        const events = data.events || [];

        // Convert Grid events to activities
        const mappedActivities: Activity[] = events.slice(0, 5).map((event: any, index: number) => ({
          id: index,
          type: event.event_type || 'unknown',
          title: formatEventTitle(event.event_type),
          description: event.details?.content || 'Grid event occurred',
          time: formatTimestamp(event.timestamp),
          icon: getEventIcon(event.event_type),
          color: getEventColor(event.event_type),
        }));

        setActivities(mappedActivities);
        setError(null);
      } else {
        setError('Unable to fetch recent activities');
        setActivities([]);
      }
    } catch (err) {
      console.error('Failed to fetch activities:', err);
      setError('Service unavailable');
      setActivities([]);
    } finally {
      setLoading(false);
    }
  };

  const formatEventTitle = (eventType: string): string => {
    const titles: Record<string, string> = {
      'AgentRegistered': 'Grid Agent Registered',
      'AgentHeartbeat': 'Agent Heartbeat',
      'SpawnSucceeded': 'Storage Node Spawned',
      'SpawnFailed': 'Node Spawn Failed',
      'NodeCrashed': 'Storage Node Crashed',
      'unknown': 'System Event',
    };
    return titles[eventType] || eventType;
  };

  const getEventIcon = (eventType: string): React.ReactNode => {
    const icons: Record<string, React.ReactNode> = {
      'AgentRegistered': <StartIcon />,
      'AgentHeartbeat': <DataIcon />,
      'SpawnSucceeded': <StartIcon />,
      'SpawnFailed': <ErrorIcon />,
      'NodeCrashed': <StopIcon />,
      'unknown': <QueryIcon />,
    };
    return icons[eventType] || <QueryIcon />;
  };

  const getEventColor = (eventType: string): 'success' | 'primary' | 'info' | 'warning' | 'error' => {
    const colors: Record<string, 'success' | 'primary' | 'info' | 'warning' | 'error'> = {
      'AgentRegistered': 'success',
      'AgentHeartbeat': 'info',
      'SpawnSucceeded': 'success',
      'SpawnFailed': 'error',
      'NodeCrashed': 'error',
      'unknown': 'primary',
    };
    return colors[eventType] || 'primary';
  };

  const formatTimestamp = (timestamp: string): string => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now.getTime() - date.getTime();
      const minutes = Math.floor(diff / 60000);
      const hours = Math.floor(diff / 3600000);

      if (minutes < 1) return 'Just now';
      if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
      if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
      return date.toLocaleDateString();
    } catch {
      return timestamp;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Alert severity="warning" sx={{ mt: 2 }}>
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (activities.length === 0) {
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            No recent activity. System events will appear here once the Grid is active.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Recent Activity
        </Typography>

        <Stack spacing={2} mt={2}>
          {activities.map((activity, index) => (
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