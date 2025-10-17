import React from 'react';
import { Typography, Card, CardContent } from '@mui/material';

export const Analytics: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          Performance Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Advanced analytics and insights dashboard coming soon...
        </Typography>
      </CardContent>
    </Card>
  );
};