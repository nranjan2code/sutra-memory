import React from 'react';
import { Typography, Card, CardContent } from '@mui/material';

export const Reasoning: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          Reasoning Engine
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Reasoning paths and query interface coming soon...
        </Typography>
      </CardContent>
    </Card>
  );
};