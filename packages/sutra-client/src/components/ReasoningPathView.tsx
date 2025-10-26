/**
 * Reasoning Path Visualization
 * 
 * Component that displays reasoning paths used to generate an answer.
 * Shows the knowledge graph with highlighted paths and confidence scores.
 */

import React, { useState, lazy, Suspense } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Collapse,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  Psychology,
  TrendingFlat,
  CheckCircle,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { graphApi } from '../services/api';
import { MessageGraphResponse } from '../types/api';

// Lazy load KnowledgeGraph for better initial bundle size
const KnowledgeGraph = lazy(() => import('./KnowledgeGraph'))
interface ReasoningPathViewProps {
  messageId: string;
  conversationId: string;
  confidence?: number;
}

type ConfidenceColor = 'success' | 'warning' | 'error';

/**
 * Get confidence color
 */
function getConfidenceColor(confidence: number): ConfidenceColor {
  if (confidence >= 0.9) return 'success';
  if (confidence >= 0.7) return 'warning';
  return 'error';
}

/**
 * Get confidence label
 */
function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.9) return 'High Confidence';
  if (confidence >= 0.7) return 'Medium Confidence';
  return 'Low Confidence';
}

export const ReasoningPathView: React.FC<ReasoningPathViewProps> = ({
  messageId,
  conversationId,
  confidence = 0,
}) => {
  const [expanded, setExpanded] = useState(false);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  // Fetch graph data
  const {
    data: graphData,
    isLoading,
    error,
  } = useQuery<MessageGraphResponse>({
    queryKey: ['message-graph', messageId],
    queryFn: () =>
      graphApi.getMessageGraph({
        message_id: messageId,
        conversation_id: conversationId,
        max_depth: 2,
      }),
    enabled: expanded, // Only fetch when expanded
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
  });

  const handleToggle = () => {
    setExpanded(!expanded);
  };

  const handleNodeClick = (nodeId: string) => {
    setSelectedNode(nodeId === selectedNode ? null : nodeId);
  };

  const conceptCount = graphData?.graph.concept_count || 0;
  const edgeCount = graphData?.graph.edge_count || 0;
  const displayConfidence = graphData?.confidence || confidence;

  return (
    <Card
      variant="outlined"
      sx={{
        mt: 2,
        borderColor: 'divider',
        backgroundColor: 'background.paper',
      }}
    >
      <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
        {/* Header */}
        <Box
          display="flex"
          alignItems="center"
          justifyContent="space-between"
          sx={{ cursor: 'pointer' }}
          onClick={handleToggle}
        >
          <Box display="flex" alignItems="center" gap={1}>
            <Psychology color="primary" />
            <Typography variant="subtitle2" fontWeight="medium">
              Reasoning Path
            </Typography>
            {displayConfidence > 0 && (
              <Chip
                label={getConfidenceLabel(displayConfidence)}
                size="small"
                color={getConfidenceColor(displayConfidence)}
                sx={{ height: 22, fontSize: '0.75rem' }}
              />
            )}
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            {expanded && !isLoading && graphData && (
              <Typography variant="caption" color="text.secondary">
                {conceptCount} concepts, {edgeCount} connections
              </Typography>
            )}
            <IconButton size="small">
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>

        {/* Expandable content */}
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          <Divider sx={{ my: 2 }} />

          {/* Loading state */}
          {isLoading && (
            <Box display="flex" justifyContent="center" py={4}>
              <CircularProgress size={40} />
            </Box>
          )}

          {/* Error state */}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              Failed to load reasoning graph: {(error as Error).message}
            </Alert>
          )}

          {/* Graph visualization */}
          {!isLoading && !error && graphData && (
            <Box>
              {/* Reasoning steps (if available) */}
              {graphData.reasoning_paths && graphData.reasoning_paths.length > 0 && (
                <Box mb={2}>
                  <Typography
                    variant="caption"
                    fontWeight="medium"
                    display="block"
                    mb={1}
                    color="text.secondary"
                  >
                    Reasoning Steps:
                  </Typography>
                  <List dense sx={{ p: 0 }}>
                    {graphData.reasoning_paths.map((path: unknown, index: number) => {
                      const pathObj = path as { explanation?: string };
                      return (
                        <ListItem key={index} sx={{ py: 0.5, px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            {index === graphData.reasoning_paths.length - 1 ? (
                              <CheckCircle fontSize="small" color="success" />
                            ) : (
                              <TrendingFlat fontSize="small" color="action" />
                            )}
                          </ListItemIcon>
                          <ListItemText
                            primary={
                              typeof path === 'string'
                                ? path
                                : pathObj.explanation || `Step ${index + 1}`
                            }
                            primaryTypographyProps={{
                              variant: 'caption',
                              color: 'text.secondary',
                            }}
                          />
                        </ListItem>
                      );
                    })}
                  </List>
                </Box>
              )}

              {/* Knowledge graph */}
              <Box mt={2}>
                <Suspense fallback={
                  <Box
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    height={500}
                    sx={{ backgroundColor: 'background.default', borderRadius: 2 }}
                  >
                    <CircularProgress />
                  </Box>
                }>
                  <KnowledgeGraph
                    graphData={graphData.graph}
                    onNodeClick={handleNodeClick}
                    height={500}
                  />
                </Suspense>
              </Box>

              {/* Selected node detail */}
              {selectedNode && (
                <Box mt={2}>
                  <Typography variant="caption" fontWeight="medium" display="block" mb={1}>
                    Selected Concept:
                  </Typography>
                  {(() => {
                    const node = graphData.graph.nodes.find((n) => n.id === selectedNode);
                    if (!node) return null;
                    return (
                      <Card variant="outlined">
                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                          <Typography variant="body2">{node.content}</Typography>
                          {node.confidence && (
                            <Chip
                              label={`${(node.confidence * 100).toFixed(0)}% confidence`}
                              size="small"
                              color={getConfidenceColor(node.confidence)}
                              sx={{ mt: 1, height: 20, fontSize: '0.7rem' }}
                            />
                          )}
                        </CardContent>
                      </Card>
                    );
                  })()}
                </Box>
              )}

              {/* Graph statistics */}
              <Box
                mt={2}
                p={1.5}
                sx={{
                  backgroundColor: 'action.hover',
                  borderRadius: 1,
                }}
              >
                <Typography variant="caption" display="block" color="text.secondary">
                  This answer was generated using {conceptCount} concepts and {edgeCount}{' '}
                  associations from the knowledge graph.
                </Typography>
                <Typography variant="caption" display="block" color="text.secondary" mt={0.5}>
                  Confidence Score: {(displayConfidence * 100).toFixed(1)}%
                </Typography>
              </Box>
            </Box>
          )}
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default ReasoningPathView;
