import React from 'react';
import { Typography, Card, CardContent } from '@mui/material';

export const Settings: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          System configuration and preferences coming soon...
        </Typography>
      </CardContent>
    </Card>
  );
};