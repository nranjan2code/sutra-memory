/**
 * GraphCanvas Component
 * Main visualization area with adaptive rendering
 */

import { useState, useEffect, useRef } from 'react';
import { Text, GraphListView, type GraphNode } from '@sutra/ui-framework';
import type { Node, Edge } from '@types/graph';
import type { DeviceType } from '@types/render';
import './GraphCanvas.css';

interface GraphCanvasProps {
  nodes: Node[];
  edges: Edge[];
  selectedNode: Node | null;
  onSelectNode: (node: Node) => void;
  deviceType: DeviceType;
  loading: boolean;
}

export default function GraphCanvas({
  nodes,
  edges,
  selectedNode,
  onSelectNode,
  deviceType,
  loading,
}: GraphCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight,
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Convert Node to GraphNode format for UI framework
  const graphNodes: GraphNode[] = nodes.map(node => ({
    id: node.id,
    content: node.content,
    confidence: node.confidence,
    strength: node.strength,
    edgeCount: node.edgeCount,
    accessCount: node.accessCount,
    metadata: node.metadata,
  }));

  // Adaptive rendering strategy
  const renderMode = selectRenderMode(deviceType, nodes.length);

  if (loading) {
    return (
      <div className="graph-canvas-loading">
        <Text variant="h5" color="primary" className="loading-text">
          LOADING GRAPH...
        </Text>
        <div className="loading-spinner holo-pulse" />
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="graph-canvas-empty">
        <Text variant="h5" color="secondary">
          No nodes loaded
        </Text>
        <Text variant="body2" color="tertiary">
          Load a storage.dat file to visualize the graph
        </Text>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="graph-canvas">
      {renderMode === 'list' && (
        <GraphListView
          nodes={graphNodes}
          selectedNodeId={selectedNode?.id}
          onSelectNode={(node) => {
            const fullNode = nodes.find(n => n.id === node.id);
            if (fullNode) onSelectNode(fullNode);
          }}
          containerWidth={dimensions.width}
          containerHeight={dimensions.height}
        />
      )}

      {renderMode === 'force2d' && (
        <div className="graph-canvas-placeholder">
          <Text variant="h6" color="primary">
            Force-Directed 2D View
          </Text>
          <Text variant="body2" color="secondary">
            {nodes.length} nodes, {edges.length} edges
          </Text>
          <Text variant="caption" color="secondary">
            Implementation coming soon (D3.js force simulation)
          </Text>
        </div>
      )}

      {renderMode === '3d' && (
        <div className="graph-canvas-placeholder">
          <Text variant="h6" color="primary">
            3D Immersive View
          </Text>
          <Text variant="body2" color="secondary">
            {nodes.length} nodes, {edges.length} edges
          </Text>
          <Text variant="caption" color="secondary">
            Implementation coming soon (Three.js)
          </Text>
        </div>
      )}
    </div>
  );
}

// Adaptive rendering logic
function selectRenderMode(deviceType: DeviceType, nodeCount: number): 'list' | 'force2d' | '3d' {
  // Mobile: Always list view
  if (deviceType === 'mobile') {
    return 'list';
  }

  // Tablet: List for small graphs, Force2D for larger
  if (deviceType === 'tablet') {
    return nodeCount < 50 ? 'list' : 'force2d';
  }

  // Desktop: Adaptive based on count
  if (deviceType === 'desktop') {
    if (nodeCount < 20) return 'list';
    if (nodeCount < 500) return 'force2d';
    return 'force2d'; // Will upgrade to 3D later
  }

  // 4K: 3D for large graphs
  if (deviceType === '4k') {
    return nodeCount < 50 ? 'force2d' : '3d';
  }

  // Default
  return 'list';
}
