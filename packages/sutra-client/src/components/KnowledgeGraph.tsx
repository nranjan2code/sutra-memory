/**
 * Knowledge Graph Visualization Component
 * 
 * Interactive visualization of reasoning paths and concept relationships
 * using ReactFlow for rendering.
 */

import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Position,
  MarkerType,
  ConnectionLineType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Paper,
  Typography,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Psychology,
  SmartToy,
} from '@mui/icons-material';

export interface GraphNodeData {
  id: string;
  content: string;
  type: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

export interface GraphEdgeData {
  source: string;
  target: string;
  type: string;
  strength?: number;
  metadata?: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNodeData[];
  edges: GraphEdgeData[];
  concept_count: number;
  edge_count: number;
}

interface KnowledgeGraphProps {
  graphData: GraphData;
  loading?: boolean;
  error?: string | null;
  highlightedPaths?: string[][]; // Array of concept ID paths to highlight
  onNodeClick?: (nodeId: string) => void;
  height?: number | string;
}

/**
 * Get node color based on type and confidence
 */
function getNodeColor(type: string, confidence?: number): string {
  if (type === 'central_concept') return '#6750A4'; // Primary
  if (type === 'domain_concept') return '#7950F2'; // Purple variant
  if (type === 'path_concept') {
    // Color based on confidence
    if (confidence && confidence >= 0.9) return '#2E7D32'; // Green
    if (confidence && confidence >= 0.7) return '#ED6C02'; // Orange
    return '#D32F2F'; // Red
  }
  if (type === 'associated_concept') return '#625B71'; // Secondary
  return '#79747E'; // Outline
}

/**
 * Get node size based on type
 */
function getNodeSize(type: string): { width: number; height: number } {
  if (type === 'central_concept') return { width: 180, height: 80 };
  if (type === 'domain_concept') return { width: 150, height: 70 };
  if (type === 'path_concept') return { width: 140, height: 65 };
  return { width: 120, height: 60 };
}

/**
 * Custom node component
 */
interface CustomNodeData {
  content: string;
  type: string;
  confidence?: number;
  metadata?: Record<string, unknown>;
}

const CustomNode: React.FC<{ data: CustomNodeData }> = ({ data }) => {
  const { content, type, confidence } = data;
  const color = getNodeColor(type, confidence);
  const size = getNodeSize(type);
  
  return (
    <Paper
      elevation={4}
      sx={{
        width: size.width,
        minHeight: size.height,
        p: 1.5,
        borderRadius: 2,
        backgroundColor: 'background.paper',
        border: `2px solid ${color}`,
        cursor: 'pointer',
        '&:hover': {
          boxShadow: 6,
          transform: 'scale(1.05)',
        },
        transition: 'all 0.2s ease',
      }}
    >
      <Box display="flex" alignItems="flex-start" gap={1}>
        {type === 'central_concept' ? (
          <Psychology fontSize="small" sx={{ color }} />
        ) : (
          <SmartToy fontSize="small" sx={{ color }} />
        )}
        <Box flex={1}>
          <Typography
            variant="caption"
            sx={{
              fontSize: '0.75rem',
              lineHeight: 1.4,
              display: '-webkit-box',
              WebkitLineClamp: 3,
              WebkitBoxOrient: 'vertical',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {content}
          </Typography>
          {confidence !== undefined && (
            <Chip
              label={`${(confidence * 100).toFixed(0)}%`}
              size="small"
              sx={{
                mt: 0.5,
                height: 18,
                fontSize: '0.65rem',
                backgroundColor: color,
                color: 'white',
              }}
            />
          )}
        </Box>
      </Box>
    </Paper>
  );
};

const nodeTypes = {
  custom: CustomNode,
};

/**
 * Layout nodes using force-directed algorithm (simplified Dagre-like layout)
 */
function layoutNodes(nodes: GraphNodeData[], edges: GraphEdgeData[]): Node[] {
  const flowNodes: Node[] = [];
  const edgeMap = new Map<string, string[]>();
  
  // Build adjacency list
  edges.forEach(edge => {
    if (!edgeMap.has(edge.source)) {
      edgeMap.set(edge.source, []);
    }
    edgeMap.get(edge.source)!.push(edge.target);
  });
  
  // Find root nodes (no incoming edges)
  const incomingCount = new Map<string, number>();
  nodes.forEach(n => incomingCount.set(n.id, 0));
  edges.forEach(e => incomingCount.set(e.target, (incomingCount.get(e.target) || 0) + 1));
  
  const roots = nodes.filter(n => incomingCount.get(n.id) === 0);
  
  // BFS layout
  const visited = new Set<string>();
  const levels = new Map<string, number>();
  const queue: Array<{ id: string; level: number }> = roots.map(r => ({ id: r.id, level: 0 }));
  
  while (queue.length > 0) {
    const { id, level } = queue.shift()!;
    if (visited.has(id)) continue;
    
    visited.add(id);
    levels.set(id, level);
    
    const neighbors = edgeMap.get(id) || [];
    neighbors.forEach(neighbor => {
      if (!visited.has(neighbor)) {
        queue.push({ id: neighbor, level: level + 1 });
      }
    });
  }
  
  // Position nodes
  const levelGroups = new Map<number, string[]>();
  nodes.forEach(node => {
    const level = levels.get(node.id) || 0;
    if (!levelGroups.has(level)) {
      levelGroups.set(level, []);
    }
    levelGroups.get(level)!.push(node.id);
  });
  
  const LEVEL_SPACING = 250;
  const NODE_SPACING = 180;
  
  nodes.forEach(node => {
    const level = levels.get(node.id) || 0;
    const nodesInLevel = levelGroups.get(level) || [];
    const indexInLevel = nodesInLevel.indexOf(node.id);
    
    const x = indexInLevel * NODE_SPACING - (nodesInLevel.length * NODE_SPACING) / 2 + 400;
    const y = level * LEVEL_SPACING + 50;
    
    flowNodes.push({
      id: node.id,
      type: 'custom',
      position: { x, y },
      data: {
        content: node.content,
        type: node.type,
        confidence: node.confidence,
        metadata: node.metadata,
      },
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
    });
  });
  
  return flowNodes;
}

/**
 * Convert graph edges to ReactFlow edges
 */
function layoutEdges(edges: GraphEdgeData[]): Edge[] {
  return edges.map((edge, index) => ({
    id: `edge-${edge.source}-${edge.target}-${index}`,
    source: edge.source,
    target: edge.target,
    type: ConnectionLineType.SmoothStep,
    animated: edge.type === 'reasoning_step',
    label: edge.type,
    labelStyle: { fontSize: 10, fill: '#79747E' },
    labelBgStyle: { fill: '#FEF7FF', opacity: 0.9 },
    style: {
      stroke: edge.type === 'reasoning_step' ? '#6750A4' : '#79747E',
      strokeWidth: edge.strength ? edge.strength * 2 : 1,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 20,
      height: 20,
      color: edge.type === 'reasoning_step' ? '#6750A4' : '#79747E',
    },
  }));
}

export const KnowledgeGraph: React.FC<KnowledgeGraphProps> = ({
  graphData,
  loading = false,
  error = null,
  onNodeClick,
  height = 600,
}) => {
  // Layout nodes and edges
  const flowNodes = useMemo(
    () => layoutNodes(graphData.nodes, graphData.edges),
    [graphData.nodes, graphData.edges]
  );
  
  const flowEdges = useMemo(
    () => layoutEdges(graphData.edges),
    [graphData.edges]
  );
  
  const [nodes, setNodes, onNodesChange] = useNodesState(flowNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(flowEdges);
  
  // Update nodes/edges when graphData changes
  React.useEffect(() => {
    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [flowNodes, flowEdges, setNodes, setEdges]);
  
  const handleNodeClick = useCallback(
    (_event: React.MouseEvent, node: Node) => {
      if (onNodeClick) {
        onNodeClick(node.id);
      }
    },
    [onNodeClick]
  );
  
  if (loading) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height={height}
        sx={{ backgroundColor: 'background.default', borderRadius: 2 }}
      >
        <CircularProgress />
      </Box>
    );
  }
  
  if (error) {
    return (
      <Box height={height} p={2}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }
  
  if (graphData.nodes.length === 0) {
    return (
      <Box
        display="flex"
        alignItems="center"
        justifyContent="center"
        height={height}
        sx={{ backgroundColor: 'background.default', borderRadius: 2 }}
      >
        <Typography color="text.secondary">
          No graph data available
        </Typography>
      </Box>
    );
  }
  
  return (
    <Box height={height} sx={{ position: 'relative', borderRadius: 2, overflow: 'hidden' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        style={{ backgroundColor: '#FEF7FF' }}
      >
        <Background />
        <Controls />
        <MiniMap
          nodeColor={(node) => {
            const data = node.data as CustomNodeData;
            return getNodeColor(data.type, data.confidence);
          }}
          style={{
            backgroundColor: '#FFFFFF',
          }}
        />
      </ReactFlow>
      
      {/* Graph info overlay */}
      <Paper
        elevation={2}
        sx={{
          position: 'absolute',
          top: 16,
          right: 16,
          p: 2,
          backgroundColor: 'background.paper',
          opacity: 0.95,
        }}
      >
        <Typography variant="caption" display="block" color="text.secondary">
          Concepts: {graphData.concept_count}
        </Typography>
        <Typography variant="caption" display="block" color="text.secondary">
          Associations: {graphData.edge_count}
        </Typography>
      </Paper>
    </Box>
  );
};

export default KnowledgeGraph;
