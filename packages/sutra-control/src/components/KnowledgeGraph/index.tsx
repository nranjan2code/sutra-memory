import React from 'react';
import { Typography, Card, CardContent } from '@mui/material';

export const KnowledgeGraph: React.FC = () => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h4" gutterBottom>
          Knowledge Graph
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Interactive knowledge graph visualization coming soon...
        </Typography>
      </CardContent>
    </Card>
  );
};